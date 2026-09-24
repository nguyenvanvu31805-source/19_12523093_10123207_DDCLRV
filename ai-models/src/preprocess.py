"""
Module tiền xử lý dữ liệu cho bài toán Wine Quality Prediction using Regression.
Logic bám sát notebook 02_preprocess.ipynb.
"""

from pathlib import Path
from typing import Tuple, Union
import zipfile

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# Danh sách 11 thuộc tính đầu vào (features) theo đúng thứ tự
FEATURES = [
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
    "alcohol",
]

# Tên biến mục tiêu (target)
TARGET = "quality"


def load_dataset(data_path: Union[str, Path]) -> pd.DataFrame:
    """
    Đọc dữ liệu từ đường dẫn tệp CSV hoặc ZIP.

    Hỗ trợ:
    - Đường dẫn tệp .csv trực tiếp.
    - Đường dẫn tệp .zip chứa file .csv bên trong.

    Parameters:
    -----------
    data_path : str hoặc Path
        Đường dẫn tới tệp dữ liệu.

    Returns:
    --------
    pd.DataFrame
        DataFrame chứa dữ liệu đã nạp.
    """
    path = Path(data_path)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy tệp dữ liệu tại: {path}")

    if path.suffix == ".zip":
        with zipfile.ZipFile(path, "r") as z:
            csv_files = [f for f in z.namelist() if f.endswith(".csv")]
            if not csv_files:
                raise FileNotFoundError(f"Không tìm thấy tệp .csv nào trong zip: {path}")
            # Lấy file csv đầu tiên tìm thấy
            with z.open(csv_files[0]) as f:
                df = pd.read_csv(f)
    elif path.suffix == ".csv":
        df = pd.read_csv(path)
    else:
        raise ValueError(f"Định dạng tệp không được hỗ trợ ({path.suffix}). Vui lòng dùng .csv hoặc .zip.")

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Loại bỏ các dòng trùng lặp trong dataframe và đặt lại chỉ số (index).
    Khớp logic notebook 02_preprocess.ipynb:
    df = df.drop_duplicates().reset_index(drop=True)

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame gốc.

    Returns:
    --------
    pd.DataFrame
        DataFrame sau khi loại bỏ dòng trùng lặp.
    """
    return df.drop_duplicates().reset_index(drop=True)


def split_features_target(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Tách tập dữ liệu thành biến đầu vào X (11 features) và biến mục tiêu y (quality).

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame đã làm sạch.

    Returns:
    --------
    Tuple[pd.DataFrame, pd.Series]
        (X, y) trong đó X chứa 11 features và y là biến mục tiêu quality.
    """
    X = df[FEATURES].copy()
    y = df[TARGET].copy()
    return X, y


def split_train_test(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Chia dữ liệu thành tập huấn luyện (train) và kiểm thử (test).
    Tỷ lệ mặc định: 80% train / 20% test (test_size = 0.2, random_state = 42).

    Parameters:
    -----------
    X : pd.DataFrame
        Ma trận đặc trưng đầu vào.
    y : pd.Series
        Vector nhãn mục tiêu.
    test_size : float, mặc định 0.2
        Tỷ lệ phân chia tập test.
    random_state : int, mặc định 42
        Seed cố định tính ngẫu nhiên.

    Returns:
    --------
    Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]
        X_train, X_test, y_train, y_test
    """
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def build_preprocessing_pipeline() -> Pipeline:
    """
    Tạo pipeline tiền xử lý dữ liệu:
    1. SimpleImputer(strategy="median"): Điền các giá trị thiếu bằng trung vị (median).
    2. StandardScaler(): Chuẩn hóa các thuộc tính về trung bình 0, độ lệch chuẩn 1.

    Returns:
    --------
    Pipeline
        Pipeline tiền xử lý của scikit-learn.
    """
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])


if __name__ == "__main__":
    try:
        print("--- Kiểm tra module preprocess ---")
        print(f"FEATURES ({len(FEATURES)}): {FEATURES}")
        print(f"TARGET: {TARGET}")
        pipeline = build_preprocessing_pipeline()
        print("Preprocessing Pipeline cấu hình thành công:")
        print(pipeline)
    except UnicodeEncodeError:
        print("--- Kiem tra module preprocess ---")
        print(f"FEATURES ({len(FEATURES)}): {FEATURES}")
        print(f"TARGET: {TARGET}")
        pipeline = build_preprocessing_pipeline()
        print("Preprocessing Pipeline cau hinh thanh cong:")
        print(pipeline)
