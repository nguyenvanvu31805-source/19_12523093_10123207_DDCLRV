import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
import time
from typing import Any, Optional
import uuid

import joblib
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware

from schemas import HealthResponse, ModelInfoResponse, PredictResponse, WineFeatures

# Thiết lập ghi log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("wine_quality_api")

# Đường dẫn đến mô hình và schema
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = (BASE_DIR.parent / "models" / "model.joblib").resolve()
SCHEMA_PATH = (BASE_DIR.parent / "models" / "schema.json").resolve()
METADATA_PATH = (BASE_DIR.parent / "models" / "metadata.json").resolve()

# Biến toàn cục lưu model, schema và metadata
model: Optional[Any] = None
schema_data: Optional[dict] = None
metadata_data: Optional[dict] = None


def load_model_and_schema():
    """
    Nạp model, schema và metadata đã huấn luyện từ Colab.
    Nếu file chưa tồn tại, ghi log cảnh báo rõ ràng thay vì tạo model giả.
    """
    global model, schema_data, metadata_data

    # 1. Nạp model
    if MODEL_PATH.exists():
        try:
            model = joblib.load(MODEL_PATH)
            logger.info("Model da duoc nap thanh cong tu: %s", MODEL_PATH)
        except Exception as e:
            logger.error("Loi khi doc model tu %s: %s", MODEL_PATH, e)
            model = None
    else:
        logger.warning(
            "Khong tim thay model tai '%s'. "
            "Vui long copy 'model.joblib' tu Google Colab vao thu muc 'ai-models/models/'.",
            MODEL_PATH
        )

    # 2. Nạp schema nếu có
    if SCHEMA_PATH.exists():
        try:
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema_data = json.load(f)
            logger.info("Schema da duoc nap thanh cong tu: %s", SCHEMA_PATH)
        except Exception as e:
            logger.warning("Khong the doc schema tu %s: %s", SCHEMA_PATH, e)
            schema_data = None

    # 3. Nạp metadata nếu có
    if METADATA_PATH.exists():
        try:
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                metadata_data = json.load(f)
            logger.info("Metadata da duoc nap thanh cong tu: %s", METADATA_PATH)
        except Exception as e:
            logger.warning("Khong the doc metadata tu %s: %s", METADATA_PATH, e)
            metadata_data = None



@asynccontextmanager
async def lifespan(app: FastAPI):
    """Quản lý vòng đời khởi động và kết thúc của FastAPI application."""
    load_model_and_schema()
    yield


# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="Wine Quality Regression AI Service",
    description="API dự đoán điểm chất lượng rượu vang đỏ (Red Wine) bằng mô hình Machine Learning",
    version="1.0.0",
    lifespan=lifespan
)

# Cấu hình CORS để cho phép frontend gọi API
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
    - Đính kèm X-Request-ID vào response header trả về.
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


@app.get("/", summary="Trang chủ AI Service")
def root():
    """Endpoint thông báo trạng thái hoạt động của AI Service."""
    return {
        "message": "AI Service Wine Quality Regression đang chạy",
        "model_loaded": model is not None,
        "endpoints": {
            "health": "/health",
            "model_info": "/model-info",
            "predict": "/predict",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, summary="Kiểm tra sức khỏe dịch vụ")
def health():
    """Endpoint kiểm tra tình trạng dịch vụ (health check)."""
    return HealthResponse(status="ok")


@app.get("/model-info", response_model=ModelInfoResponse, summary="Thông tin mô hình AI")
def get_model_info():
    """
    Endpoint trả về thông tin chi tiết của mô hình đang phục vụ:
    - model name, model version, task, target
    - metrics (MAE, MSE, RMSE, R2)
    - best parameters
    - dataset information
    - training date & libraries
    Đọc trực tiếp từ tệp metadata.json đã nạp.
    """
    global metadata_data

    # Thử nạp lại nếu metadata_data chưa có trong bộ nhớ
    if metadata_data is None and METADATA_PATH.exists():
        try:
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                metadata_data = json.load(f)
        except Exception as e:
            logger.error("Lỗi khi đọc metadata từ %s: %s", METADATA_PATH, e)

    if metadata_data is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Metadata chưa sẵn sàng: Không tìm thấy hoặc không thể đọc tệp metadata tại '{METADATA_PATH}'."
            )
        )

    return metadata_data



@app.post("/predict", response_model=PredictResponse, summary="Dự đoán chất lượng rượu vang")
def predict(features: WineFeatures, request: Request):
    """
    Dự đoán chất lượng rượu vang từ 11 đặc trưng hóa lý:
    - fixed acidity
    - volatile acidity
    - citric acid
    - residual sugar
    - chlorides
    - free sulfur dioxide
    - total sulfur dioxide
    - density
    - pH
    - sulphates
    - alcohol

    Quy trình: JSON request -> Pydantic Validation -> DataFrame -> model.predict()
    KHÔNG tự tiền xử lý riêng vì model.joblib đã chứa đầy đủ Pipeline (SimpleImputer + StandardScaler).
    """
    global model

    req_id = (
        getattr(request.state, "request_id", None)
        if request and hasattr(request, "state")
        else None
    ) or (
        request.headers.get("X-Request-ID")
        if request and hasattr(request, "headers")
        else None
    ) or "unknown"

    # Nếu model chưa được nạp, thử nạp lại (phòng trường hợp người dùng vừa copy file vào)
    if model is None:
        load_model_and_schema()

    # Nếu vẫn chưa có model, trả về lỗi HTTP 503 thông báo rõ ràng
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Model chưa sẵn sàng: Không tìm thấy model tại '{MODEL_PATH}'. "
                "Vui lòng copy file 'model.joblib' từ Google Colab vào thư mục 'ai-models/models/'."
            )
        )

    try:
        # Chuyển dữ liệu sang DataFrame với đúng 11 features theo đúng thứ tự
        df = features.to_dataframe()

        # Gọi trực tiếp pipeline đã đóng gói trong model.joblib
        raw_prediction = model.predict(df)[0]
        pred_value = round(float(raw_prediction), 4)
        logger.info("request_id=%s prediction=%s", req_id, pred_value)

        # Trả về kết quả dự đoán (làm tròn 4 số thập phân)
        return PredictResponse(prediction=pred_value)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("request_id=%s Lỗi khi thực hiện dự đoán: %s", req_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi thực hiện dự đoán: {str(e)}"
        )
