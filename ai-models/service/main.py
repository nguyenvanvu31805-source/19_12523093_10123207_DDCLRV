import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Optional

import joblib
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from schemas import HealthResponse, PredictResponse, WineFeatures

# Thiết lập ghi log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("wine_quality_api")

# Đường dẫn đến mô hình và schema
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = (BASE_DIR.parent / "models" / "model.joblib").resolve()
SCHEMA_PATH = (BASE_DIR.parent / "models" / "schema.json").resolve()

# Biến toàn cục lưu model và schema
model: Optional[Any] = None
schema_data: Optional[dict] = None


def load_model_and_schema():
    """
    Nạp model và schema đã huấn luyện từ Colab.
    Nếu file chưa tồn tại, ghi log cảnh báo rõ ràng thay vì tạo model giả.
    """
    global model, schema_data

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
)


@app.get("/", summary="Trang chủ AI Service")
def root():
    """Endpoint thông báo trạng thái hoạt động của AI Service."""
    return {
        "message": "AI Service Wine Quality Regression đang chạy",
        "model_loaded": model is not None,
        "endpoints": {
            "health": "/health",
            "predict": "/predict",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthResponse, summary="Kiểm tra sức khỏe dịch vụ")
def health():
    """Endpoint kiểm tra tình trạng dịch vụ (health check)."""
    return HealthResponse(status="ok")


@app.post("/predict", response_model=PredictResponse, summary="Dự đoán chất lượng rượu vang")
def predict(features: WineFeatures):
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

        # Trả về kết quả dự đoán (làm tròn 4 số thập phân)
        return PredictResponse(prediction=round(float(raw_prediction), 4))
    except Exception as e:
        logger.error("Lỗi khi thực hiện dự đoán: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi thực hiện dự đoán: {str(e)}"
        )
