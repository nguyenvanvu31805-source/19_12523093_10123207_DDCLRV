from datetime import datetime, timezone
import logging
import os
import time
from typing import Any, Dict, List, Optional
import uuid

from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
import httpx
from pymongo import MongoClient

from schemas import HealthResponse, HistoryItem, HistoryResponse, PredictResponse, WineFeatures

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("wine_quality_backend")

# URL của AI Service lấy từ biến môi trường, mặc định kết nối cục bộ
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://127.0.0.1:8000").rstrip("/")

# Cấu hình MongoDB lấy từ biến môi trường
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://127.0.0.1:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "wine_quality_db")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "predictions")

# Biến toàn cục lưu kết nối MongoDB (lazy initialization)
mongo_client: Optional[MongoClient] = None


def get_mongo_collection():
    """Lấy collection MongoDB với thiết lập timeout ngắn để không làm treo ứng dụng nếu DB chưa chạy."""
    global mongo_client
    if mongo_client is None:
        mongo_client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=2000)
    db = mongo_client[MONGODB_DATABASE]
    return db[MONGODB_COLLECTION]


def save_prediction_history(input_data: dict, prediction: float) -> None:
    """Lưu bản ghi lịch sử dự đoán vào MongoDB. Không để lỗi MongoDB ảnh hưởng tới kết quả trả về người dùng."""
    try:
        collection = get_mongo_collection()
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input": input_data,
            "prediction": prediction
        }
        collection.insert_one(record)
        logger.info("Đã lưu lịch sử dự đoán vào MongoDB thành công")
    except Exception as e:
        logger.error("Không thể lưu lịch sử vào MongoDB: %s", e)


app = FastAPI(
    title="Wine Quality Prediction Backend API",
    description="Backend API trung gian chuyển tiếp yêu cầu từ Frontend tới AI Service và lưu lịch sử qua MongoDB",
    version="1.1.0"
)

# Cấu hình CORS để Frontend tương tác được với Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.middleware("http")
async def request_id_and_logging_middleware(request: Request, call_next):
    """
    Middleware xử lý request_id và ghi log có cấu trúc:
    - Đọc X-Request-ID từ incoming request header, nếu không có sẽ sinh UUID4 mới.
    - Gán vào request.state.request_id để các handler bên trong có thể truy xuất.
    - Log thời điểm bắt đầu request: request_id, method, path, status=start.
    - Đo thời gian xử lý (duration_ms).
    - Đính kèm X-Request-ID vào response header trả về cho Client.
    - Log khi hoàn thành request: request_id, method, path, status_code, duration_ms.
    """
    req_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    request.state.request_id = req_id
    start_time = time.time()
    logger.info("request_id=%s method=%s path=%s status=start", req_id, request.method, request.url.path)
    try:
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = req_id
        logger.info(
            "request_id=%s method=%s path=%s status=%s duration_ms=%s",
            req_id, request.method, request.url.path, response.status_code, duration_ms
        )
        return response
    except Exception as exc:
        duration_ms = round((time.time() - start_time) * 1000, 2)
        logger.error(
            "request_id=%s method=%s path=%s status=error duration_ms=%s error=%s",
            req_id, request.method, request.url.path, duration_ms, exc
        )
        raise


@app.get("/", summary="Trang chủ Backend")
def root() -> Dict[str, Any]:
    """Endpoint thông báo Backend đang hoạt động."""
    return {
        "message": "Wine Quality Backend is running",
        "ai_service_url": AI_SERVICE_URL,
        "mongodb_url": MONGODB_URL,
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "api_predict": "/api/predict",
            "api_history": "/api/history",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, summary="Kiểm tra sức khỏe Backend")
@app.get("/api/health", response_model=HealthResponse, summary="Kiểm tra sức khỏe Backend (API v1)")
def health() -> HealthResponse:
    """Endpoint kiểm tra Backend đang hoạt động bình thường."""
    return HealthResponse(status="ok")


async def handle_prediction(features: WineFeatures, request: Optional[Request] = None) -> PredictResponse:
    """
    Hàm xử lý chung cho dự đoán:
    1. Tiếp nhận đúng 11 features từ Client/Frontend, validate qua Pydantic.
    2. Chuyển tiếp (forward) sang AI Service qua HTTP POST /predict kèm header X-Request-ID.
    3. Lưu bản ghi (timestamp, input, prediction) vào MongoDB.
    """
    req_id = (
        getattr(request.state, "request_id", None)
        if request and hasattr(request, "state")
        else None
    ) or (
        request.headers.get("X-Request-ID")
        if request and hasattr(request, "headers")
        else None
    ) or uuid.uuid4().hex

    target_url = f"{AI_SERVICE_URL}/predict"
    payload = features.to_payload()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                target_url,
                json=payload,
                headers={"X-Request-ID": req_id}
            )

        # Nếu AI Service phản hồi lỗi (ví dụ 422, 500, 503)
        if response.status_code != status.HTTP_200_OK:
            try:
                error_detail = response.json().get("detail", response.text)
            except Exception:
                error_detail = response.text
            logger.error("request_id=%s AI Service returned status %s: %s", req_id, response.status_code, error_detail)
            raise HTTPException(
                status_code=response.status_code,
                detail=f"AI Service error ({response.status_code}): {error_detail}"
            )

        data = response.json()
        if "prediction" not in data:
            logger.error("request_id=%s AI Service response missing 'prediction': %s", req_id, data)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Phản hồi từ AI Service không hợp lệ (thiếu trường 'prediction')."
            )

        pred_value = float(data["prediction"])

        # Lưu lịch sử dự đoán vào MongoDB
        save_prediction_history(payload, pred_value)

        return PredictResponse(prediction=pred_value)

    except httpx.RequestError as exc:
        logger.error("request_id=%s Không thể kết nối đến AI Service tại %s: %s", req_id, target_url, exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Không thể kết nối đến AI Service tại '{AI_SERVICE_URL}'. Vui lòng đảm bảo AI Service đang chạy."
        )


@app.post("/predict", response_model=PredictResponse, summary="Dự đoán chất lượng rượu vang")
async def predict(features: WineFeatures, request: Request) -> PredictResponse:
    """Endpoint dự đoán chất lượng rượu vang (tương thích ngược với Frontend hiện tại)."""
    return await handle_prediction(features, request)


@app.post("/api/predict", response_model=PredictResponse, summary="Dự đoán chất lượng rượu vang (API chuẩn)")
async def api_predict(features: WineFeatures, request: Request) -> PredictResponse:
    """Endpoint dự đoán chất lượng rượu vang chuẩn API v1."""
    return await handle_prediction(features, request)


@app.get("/api/history", response_model=HistoryResponse, summary="Lấy lịch sử dự đoán")
def get_history(limit: int = Query(20, ge=1, le=100, description="Số lượng bản ghi tối đa")) -> HistoryResponse:
    """
    Lấy lịch sử các lần dự đoán từ cơ sở dữ liệu MongoDB:
    - Sắp xếp giảm dần theo thời gian (timestamp mới nhất lên đầu).
    - Giới hạn số lượng bản ghi bằng query param limit (mặc định 20, tối đa 100).
    - Nếu chưa có dữ liệu: trả về {"items": [], "count": 0}.
    - Nếu không kết nối được MongoDB: trả về HTTP 503 với JSON thông báo rõ ràng.
    """
    try:
        collection = get_mongo_collection()
        cursor = collection.find(
            {},
            {"_id": 0, "timestamp": 1, "input": 1, "prediction": 1}
        ).sort("timestamp", -1).limit(limit)

        items = []
        for doc in cursor:
            items.append(HistoryItem(
                timestamp=str(doc.get("timestamp", "")),
                input=doc.get("input", {}),
                prediction=float(doc.get("prediction", 0.0))
            ))

        return HistoryResponse(items=items, count=len(items))

    except Exception as exc:
        logger.error("Lỗi khi truy vấn lịch sử từ MongoDB: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Không thể kết nối cơ sở dữ liệu MongoDB: {str(exc)}"
        )



if __name__ == "__main__":
    import uvicorn
    host = os.getenv("BACKEND_HOST", "127.0.0.1")
    port = int(os.getenv("BACKEND_PORT", "5000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
