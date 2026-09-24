import pytest
from fastapi.testclient import TestClient

from main import METADATA_PATH, MODEL_PATH, app

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
    """Kiểm tra endpoint GET / thông báo service đang chạy."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "AI Service Wine Quality Regression" in data["message"]


def test_health():
    """Kiểm tra endpoint GET /health trả về status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_missing_feature():
    """Kiểm tra validate: thiếu feature (thiếu 'alcohol') -> 422."""
    invalid_data = VALID_PAYLOAD.copy()
    del invalid_data["alcohol"]
    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422


def test_predict_invalid_data_type():
    """Kiểm tra validate: sai kiểu dữ liệu (chuỗi thay vì float) -> 422."""
    invalid_data = VALID_PAYLOAD.copy()
    invalid_data["alcohol"] = "not_a_number"
    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422


def test_predict_extra_feature():
    """Kiểm tra validate: gửi thừa feature lạ ('color') -> 422."""
    invalid_data = VALID_PAYLOAD.copy()
    invalid_data["color"] = "red"
    response = client.post("/predict", json=invalid_data)
    assert response.status_code == 422


def test_predict_model_status():
    """
    Kiểm tra endpoint POST /predict với payload hợp lệ:
    - Nếu model.joblib tồn tại: trả về 200 và có trường 'prediction'.
    - Nếu model.joblib chưa tồn tại: trả về 503 và có thông báo hướng dẫn chép file từ Colab.
    """
    response = client.post("/predict", json=VALID_PAYLOAD)

    if MODEL_PATH.exists():
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert isinstance(data["prediction"], (int, float))
    else:
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "model.joblib" in data["detail"]


def test_model_info():
    """Kiểm tra endpoint GET /model-info trả về HTTP 200, đúng định dạng JSON và đầy đủ thông tin model."""
    response = client.get("/model-info")
    if METADATA_PATH.exists():
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert data.get("model_name") == "Random Forest Regressor"
        assert data.get("model_version") == "1.0.0"
        assert data.get("task") == "regression"
        assert data.get("target") == "quality"
        assert "metrics" in data
        assert "MAE" in data["metrics"]
        assert "MSE" in data["metrics"]
        assert "RMSE" in data["metrics"]
        assert "R2" in data["metrics"]
        assert "best_parameters" in data
        assert "dataset" in data
        assert "training_date" in data
    else:
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data


def test_ai_service_request_id_preserved():
    """Kiểm tra AI Service bảo toàn và trả lại đúng header X-Request-ID từ Client."""
    custom_id = "ai-trace-custom-999"
    response = client.post("/predict", json=VALID_PAYLOAD, headers={"X-Request-ID": custom_id})
    assert response.headers.get("X-Request-ID") == custom_id


def test_ai_service_request_id_auto_generated():
    """Kiểm tra AI Service tự động sinh X-Request-ID nếu Client không truyền."""
    response = client.get("/health")
    assert response.status_code == 200
    gen_id = response.headers.get("X-Request-ID")
    assert gen_id is not None
    assert len(gen_id) > 0


def test_ai_service_model_info_request_id():
    """Kiểm tra endpoint GET /model-info trả lại đúng X-Request-ID."""
    custom_id = "info-trace-001"
    response = client.get("/model-info", headers={"X-Request-ID": custom_id})
    assert response.headers.get("X-Request-ID") == custom_id


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("=== BAT DAU KIEM THU (TEST SUITE) ===")
    test_root()
    print("[PASS] test_root: GET / thanh cong")
    test_health()
    print("[PASS] test_health: GET /health tra ve status ok")
    test_model_info()
    print("[PASS] test_model_info: GET /model-info tra ve thong tin mo hinh hop le")
    test_predict_missing_feature()
    print("[PASS] test_predict_missing_feature: Chan request thieu feature (422)")
    test_predict_invalid_data_type()
    print("[PASS] test_predict_invalid_data_type: Chan request sai kieu du lieu (422)")
    test_predict_extra_feature()
    print("[PASS] test_predict_extra_feature: Chan request chua feature la (422)")
    test_predict_model_status()
    print("[PASS] test_predict_model_status: Xu ly dung khi chua co model.joblib (503 Service Unavailable)")
    test_ai_service_request_id_preserved()
    print("[PASS] test_ai_service_request_id_preserved: X-Request-ID duoc bao toan trong response")
    test_ai_service_request_id_auto_generated()
    print("[PASS] test_ai_service_request_id_auto_generated: Tu sinh X-Request-ID khi client khong truyen")
    test_ai_service_model_info_request_id()
    print("[PASS] test_ai_service_model_info_request_id: X-Request-ID hoat dong tren /model-info")
    print("=== TAT CA CAC TEST DEU HOAN THANH XUAT SAC ===")

