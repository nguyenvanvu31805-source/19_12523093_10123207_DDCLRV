import logging
import os
from typing import Any, Dict

import httpx
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from schemas import HealthResponse, PredictResponse, WineFeatures

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("wine_quality_backend")

# URL của AI Service lấy từ biến môi trường, mặc định kết nối cục bộ
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://127.0.0.1:8000").rstrip("/")

app = FastAPI(
    title="Wine Quality Prediction Backend API",
    description="Backend API trung gian chuyển tiếp yêu cầu từ Frontend tới AI Service",
    version="1.0.0"
)

# Cấu hình CORS để Frontend tương tác được với Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="Trang chủ Backend")
def root() -> Dict[str, Any]:
    """Endpoint thông báo Backend đang hoạt động."""
    return {
        "message": "Wine Quality Backend is running",
        "ai_service_url": AI_SERVICE_URL
    }


@app.get("/health", response_model=HealthResponse, summary="Kiểm tra sức khỏe Backend")
def health() -> HealthResponse:
    """Endpoint kiểm tra Backend đang hoạt động bình thường."""
    return HealthResponse(status="ok")


@app.post("/predict", response_model=PredictResponse, summary="Dự đoán chất lượng rượu vang")
async def predict(features: WineFeatures) -> PredictResponse:
    """
    Tiếp nhận đúng 11 features từ Client/Frontend, validate qua Pydantic
    và chuyển tiếp (forward) sang AI Service qua HTTP.
    
    Backend KHÔNG tự load model và KHÔNG tự tính toán dự đoán.
    Luồng xử lý: Frontend -> Backend /predict -> AI Service /predict -> model.joblib
    """
    target_url = f"{AI_SERVICE_URL}/predict"
    payload = features.to_payload()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(target_url, json=payload)

        # Nếu AI Service phản hồi lỗi (ví dụ 422, 500, 503)
        if response.status_code != status.HTTP_200_OK:
            try:
                error_detail = response.json().get("detail", response.text)
            except Exception:
                error_detail = response.text
            logger.error("AI Service returned status %s: %s", response.status_code, error_detail)
            raise HTTPException(
                status_code=response.status_code,
                detail=f"AI Service error ({response.status_code}): {error_detail}"
            )

        data = response.json()
        if "prediction" not in data:
            logger.error("AI Service response missing 'prediction': %s", data)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Phản hồi từ AI Service không hợp lệ (thiếu trường 'prediction')."
            )

        return PredictResponse(prediction=data["prediction"])

    except httpx.RequestError as exc:
        logger.error("Không thể kết nối đến AI Service tại %s: %s", target_url, exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Không thể kết nối đến AI Service tại '{AI_SERVICE_URL}'. Vui lòng đảm bảo AI Service đang chạy."
        )


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", "5000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
