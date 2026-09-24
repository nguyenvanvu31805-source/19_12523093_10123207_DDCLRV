"""
Module huấn luyện mô hình cho bài toán Wine Quality Prediction using Regression.
Mô hình chính thức: RandomForestRegressor với các tham số tối ưu tìm được qua GridSearchCV.
Logic bám sát notebook 03_train.ipynb và 04_evaluate.ipynb.
"""

from pathlib import Path
from typing import Optional, Union

import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline

# Hỗ trợ cả import trực tiếp và import từ package
try:
    from preprocess import build_preprocessing_pipeline
except ImportError:
    from src.preprocess import build_preprocessing_pipeline


def build_model(
    n_estimators: int = 200,
    max_depth: Optional[int] = 10,
    min_samples_split: int = 2,
    random_state: int = 42,
) -> Pipeline:
    """
    Khởi tạo Pipeline scikit-learn kết hợp tiền xử lý và mô hình RandomForestRegressor:
    - Preprocessing: SimpleImputer(strategy="median") + StandardScaler()
    - Model: RandomForestRegressor với tham số tối ưu

    Parameters:
    -----------
    n_estimators : int, mặc định 200
        Số lượng cây quyết định trong rừng.
    max_depth : Optional[int], mặc định 10
        Độ sâu tối đa của mỗi cây.
    min_samples_split : int, mặc định 2
        Số lượng mẫu tối thiểu cần thiết để phân chia một nút nội bộ.
    random_state : int, mặc định 42
        Seed cố định tính ngẫu nhiên.

    Returns:
    --------
    Pipeline
        Pipeline scikit-learn hoàn chỉnh sẵn sàng huấn luyện.
    """
    preprocessing_pipeline = build_preprocessing_pipeline()

    model = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        random_state=random_state,
    )

    full_pipeline = Pipeline([
        ("preprocess", preprocessing_pipeline),
        ("model", model),
    ])

    return full_pipeline


def train_model(pipeline: Pipeline, X_train, y_train) -> Pipeline:
    """
    Huấn luyện pipeline trên tập dữ liệu train.

    Parameters:
    -----------
    pipeline : Pipeline
        Pipeline scikit-learn đã khởi tạo.
    X_train : pd.DataFrame hoặc np.ndarray
        Dữ liệu thuộc tính tập huấn luyện.
    y_train : pd.Series hoặc np.ndarray
        Giá trị mục tiêu tập huấn luyện.

    Returns:
    --------
    Pipeline
        Pipeline sau khi đã fit dữ liệu.
    """
    pipeline.fit(X_train, y_train)
    return pipeline


def save_model(model: Pipeline, output_path: Union[str, Path]) -> None:
    """
    Lưu mô hình đã huấn luyện ra file joblib.

    Parameters:
    -----------
    model : Pipeline
        Pipeline mô hình đã huấn luyện.
    output_path : str hoặc Path
        Đường dẫn file đích để lưu (ví dụ: 'models/model.joblib').
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)


if __name__ == "__main__":
    try:
        print("--- Kiểm tra module train ---")
        print("Khởi tạo cấu trúc Pipeline mô hình Random Forest Regressor:")
        pipeline = build_model()
        print(pipeline)
        print("\nLưu ý: File train.py chỉ định nghĩa cấu trúc và hàm huấn luyện.")
        print("Không tự động chạy huấn luyện để đảm bảo không ghi đè model chính thức hiện tại.")
    except UnicodeEncodeError:
        print("--- Kiem tra module train ---")
        print("Khoi tao cau truc Pipeline mo hinh Random Forest Regressor:")
        pipeline = build_model()
        print(pipeline)
        print("\nLuu y: File train.py chi dinh nghia cau truc va ham huan luyen.")
        print("Khong tu dong chay huan luyen de dam bao khong ghi de model chinh thuc hien tai.")
