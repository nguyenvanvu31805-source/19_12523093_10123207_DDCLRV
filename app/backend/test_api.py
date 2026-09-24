from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

# Dữ liệu mẫu chuẩn 11 features
VALID_PAYLOAD = {
    "fixed acidity": 7.4,
    "volatile acidity": 0.7,
    "citric acid": 0.0,
    "residual sugar": 1.9,
    "chlorides": 0.076,
    "free sulfur dioxide": 11.0,
    "total sulfur dioxide": 34.0,
    "density": 0.9978,
    "pH": 3.51,
    "sulphates": 0.56,
    "alcohol": 9.4
}


def test_root():
    """Kiểm tra endpoint GET / trả về thông báo Backend đang chạy."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Wine Quality Backend is running" in data["message"]
    assert "ai_service_url" in data


def test_health():
    """Kiểm tra endpoint GET /health trả về status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_success_mock():
    """Kiểm tra POST /predict thành công khi AI Service trả về kết quả hợp lệ."""
    mock_response = httpx.Response(
        status_code=200,
        json={"prediction": 5.0362},
        request=httpx.Request("POST", "http://127.0.0.1:8000/predict")
    )
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        response = client.post("/predict", json=VALID_PAYLOAD)

        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert data["prediction"] == 5.0362


def test_predict_missing_feature():
    """Kiểm tra validate: thiếu feature (thiếu 'alcohol') -> trả về 422."""
    invalid_data = VALID_PAYLOAD.copy()
    del invalid_data["alcohol"]
    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422


def test_predict_invalid_data_type():
    """Kiểm tra validate: sai kiểu dữ liệu (chuỗi thay vì float) -> trả về 422."""
    invalid_data = VALID_PAYLOAD.copy()
    invalid_data["alcohol"] = "invalid_string"
    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422


def test_predict_extra_feature():
    """Kiểm tra validate: gửi thừa feature lạ ('color') -> trả về 422."""
    invalid_data = VALID_PAYLOAD.copy()
    invalid_data["color"] = "red"
    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422


def test_predict_ai_service_unavailable():
    """Kiểm tra xử lý lỗi khi AI Service không chạy (lỗi kết nối mạng) -> trả về 503."""
    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused")):
        response = client.post("/predict", json=VALID_PAYLOAD)
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "Không thể kết nối đến AI Service" in data["detail"]


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=== BAT DAU KIEM THU BACKEND (TEST SUITE) ===")
    test_root()
    print("[PASS] test_root: GET / thanh cong")
    test_health()
    print("[PASS] test_health: GET /health tra ve status ok")
    test_predict_success_mock()
    print("[PASS] test_predict_success_mock: Forward prediction thanh cong")
    test_predict_missing_feature()
    print("[PASS] test_predict_missing_feature: Chan request thieu feature (422)")
    test_predict_invalid_data_type()
    print("[PASS] test_predict_invalid_data_type: Chan request sai kieu du lieu (422)")
    test_predict_extra_feature()
    print("[PASS] test_predict_extra_feature: Chan request chua feature la (422)")
    test_predict_ai_service_unavailable()
    print("[PASS] test_predict_ai_service_unavailable: Xu ly loi ket noi mang (503 Service Unavailable)")
    print("=== TAT CA CAC TEST BACKEND DEU THANH CONG ===")
