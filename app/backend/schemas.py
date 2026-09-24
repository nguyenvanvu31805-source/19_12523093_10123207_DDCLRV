from typing import List
from pydantic import BaseModel, Field

# Danh sách đúng 11 features theo đúng thứ tự huấn luyện
FEATURE_NAMES: List[str] = [
    "fixed acidity",
    "volatile acidity",
    "citric acid",
    "residual sugar",
    "chlorides",
    "free sulfur dioxide",
    "total sulfur dioxide",
    "density",
    "pH",
    "sulphates",
    "alcohol"
]

try:
    from pydantic import ConfigDict
    PYDANTIC_V2 = True
except ImportError:
    PYDANTIC_V2 = False


class WineFeatures(BaseModel):
    fixed_acidity: float = Field(..., alias="fixed acidity", description="Độ axit cố định")
    volatile_acidity: float = Field(..., alias="volatile acidity", description="Độ axit bay hơi")
    citric_acid: float = Field(..., alias="citric acid", description="Axit xitric")
    residual_sugar: float = Field(..., alias="residual sugar", description="Đường dư")
    chlorides: float = Field(..., alias="chlorides", description="Muối clorua")
    free_sulfur_dioxide: float = Field(..., alias="free sulfur dioxide", description="Khí SO2 tự do")
    total_sulfur_dioxide: float = Field(..., alias="total sulfur dioxide", description="Tổng SO2")
    density: float = Field(..., alias="density", description="Tỉ trọng")
    pH: float = Field(..., alias="pH", description="Độ pH")
    sulphates: float = Field(..., alias="sulphates", description="Lượng sunfat")
    alcohol: float = Field(..., alias="alcohol", description="Nồng độ cồn")

    if PYDANTIC_V2:
        model_config = ConfigDict(
            populate_by_name=True,
            extra="forbid",
            json_schema_extra={
                "example": {
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
            }
        )
    else:
        class Config:
            allow_population_by_field_name = True
            extra = "forbid"
            schema_extra = {
                "example": {
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
            }

    def to_payload(self) -> dict:
        """
        Chuyển dữ liệu sang payload dictionary với tên thuộc tính alias (có khoảng trắng)
        để gửi trực tiếp sang AI Service /predict.
        """
        if hasattr(self, "model_dump"):
            return self.model_dump(by_alias=True)
        return self.dict(by_alias=True)


class PredictResponse(BaseModel):
    prediction: float


class HealthResponse(BaseModel):
    status: str = "ok"
