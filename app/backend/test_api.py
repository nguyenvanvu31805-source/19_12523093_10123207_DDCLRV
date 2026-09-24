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


def test_api_predict_success_mock():
    """Kiểm tra POST /api/predict thành công khi AI Service trả về kết quả hợp lệ."""
    mock_response = httpx.Response(
        status_code=200,
        json={"prediction": 5.0362},
        request=httpx.Request("POST", "http://127.0.0.1:8000/predict")
    )
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        response = client.post("/api/predict", json=VALID_PAYLOAD)

        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert data["prediction"] == 5.0362


def test_get_history_empty_mock():
    """Kiểm tra GET /api/history trả về danh sách rỗng khi chưa có dữ liệu."""
    with patch("main.get_mongo_collection") as mock_get_col:
        mock_col = mock_get_col.return_value
        mock_find = mock_col.find.return_value
        mock_find.sort.return_value.limit.return_value = []

        response = client.get("/api/history")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "count" in data
        assert data["items"] == []
        assert data["count"] == 0


def test_get_history_with_data_mock():
    """Kiểm tra GET /api/history trả về dữ liệu đúng định dạng JSON khi có lịch sử."""
    mock_item = {
        "timestamp": "2026-09-25T01:00:00Z",
        "input": VALID_PAYLOAD,
        "prediction": 5.0362
    }
    with patch("main.get_mongo_collection") as mock_get_col:
        mock_col = mock_get_col.return_value
        mock_find = mock_col.find.return_value
        mock_find.sort.return_value.limit.return_value = [mock_item]

        response = client.get("/api/history?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["items"]) == 1
        item = data["items"][0]
        assert item["timestamp"] == "2026-09-25T01:00:00Z"
        assert item["prediction"] == 5.0362
        assert item["input"]["fixed acidity"] == 7.4


def test_get_history_mongo_unavailable():
    """Kiểm tra GET /api/history trả về HTTP 503 khi MongoDB không kết nối được."""
    with patch("main.get_mongo_collection", side_effect=Exception("MongoDB connection timeout")):
        response = client.get("/api/history")
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "MongoDB" in data["detail"]


def test_request_id_forwarded_to_ai_service():
    """Kiểm tra X-Request-ID từ Client được Backend giữ nguyên và chuyển tiếp sang AI Service."""
    mock_response = httpx.Response(
        status_code=200,
        json={"prediction": 5.0362},
        request=httpx.Request("POST", "http://127.0.0.1:8000/predict")
    )
    custom_id = "test-fe-req-trace-12345"
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        response = client.post("/predict", json=VALID_PAYLOAD, headers={"X-Request-ID": custom_id})

        assert response.status_code == 200
        assert response.headers.get("X-Request-ID") == custom_id
        # Kiểm tra Backend đã forward đúng header X-Request-ID sang AI Service
        called_headers = mock_post.call_args.kwargs.get("headers", {})
        assert called_headers.get("X-Request-ID") == custom_id


def test_request_id_auto_generated_when_missing():
    """Kiểm tra nếu Client không truyền X-Request-ID, Backend tự sinh và chuyển tiếp sang AI Service."""
    mock_response = httpx.Response(
        status_code=200,
        json={"prediction": 5.0362},
        request=httpx.Request("POST", "http://127.0.0.1:8000/predict")
    )
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        response = client.post("/predict", json=VALID_PAYLOAD)

        assert response.status_code == 200
        gen_id = response.headers.get("X-Request-ID")
        assert gen_id is not None
        assert len(gen_id) > 0
        called_headers = mock_post.call_args.kwargs.get("headers", {})
        assert called_headers.get("X-Request-ID") == gen_id


def test_request_id_header_in_health():
    """Kiểm tra middleware trả lại X-Request-ID cho tất cả các endpoint (ví dụ /health)."""
    custom_id = "health-trace-id-999"
    response = client.get("/health", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_id


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
    test_api_predict_success_mock()
    print("[PASS] test_api_predict_success_mock: POST /api/predict forward prediction thanh cong")
    test_predict_missing_feature()
    print("[PASS] test_predict_missing_feature: Chan request thieu feature (422)")
    test_predict_invalid_data_type()
    print("[PASS] test_predict_invalid_data_type: Chan request sai kieu du lieu (422)")
    test_predict_extra_feature()
    print("[PASS] test_predict_extra_feature: Chan request chua feature la (422)")
    test_predict_ai_service_unavailable()
    print("[PASS] test_predict_ai_service_unavailable: Xu ly loi ket noi mang (503 Service Unavailable)")
    test_get_history_empty_mock()
    print("[PASS] test_get_history_empty_mock: GET /api/history tra ve rong khi chua co du lieu")
    test_get_history_with_data_mock()
    print("[PASS] test_get_history_with_data_mock: GET /api/history tra ve ban ghi hop le")
    test_get_history_mongo_unavailable()
    print("[PASS] test_get_history_mongo_unavailable: Xu ly loi khi MongoDB khong kha dung (503)")
    test_request_id_forwarded_to_ai_service()
    print("[PASS] test_request_id_forwarded_to_ai_service: X-Request-ID duoc forward sang AI Service va tra ve client")
    test_request_id_auto_generated_when_missing()
    print("[PASS] test_request_id_auto_generated_when_missing: Tu sinh X-Request-ID va forward khi thieu header")
    test_request_id_header_in_health()
    print("[PASS] test_request_id_header_in_health: X-Request-ID hoat dong tren GET /health")
    print("=== TAT CA CAC TEST BACKEND DEU THANH CONG ===")

