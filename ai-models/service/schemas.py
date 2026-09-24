from typing import List
import pandas as pd
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

    def to_dataframe(self) -> pd.DataFrame:
        """
        Chuyển dữ liệu đầu vào thành DataFrame với đúng 11 features và đúng thứ tự.
        Không tự tiền xử lý bằng code ngoài vì pipeline trong model.joblib đã tích hợp sẵn.
        """
        data = {
            "fixed acidity": [self.fixed_acidity],
            "volatile acidity": [self.volatile_acidity],
            "citric acid": [self.citric_acid],
            "residual sugar": [self.residual_sugar],
            "chlorides": [self.chlorides],
            "free sulfur dioxide": [self.free_sulfur_dioxide],
            "total sulfur dioxide": [self.total_sulfur_dioxide],
            "density": [self.density],
            "pH": [self.pH],
            "sulphates": [self.sulphates],
            "alcohol": [self.alcohol]
        }
        return pd.DataFrame(data, columns=FEATURE_NAMES)


class PredictResponse(BaseModel):
    prediction: float


class HealthResponse(BaseModel):
    status: str = "ok"
