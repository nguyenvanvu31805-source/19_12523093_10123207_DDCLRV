"""
Module đánh giá mô hình cho bài toán Wine Quality Prediction using Regression.
Bao gồm các độ đo: MAE, MSE, RMSE, R2.
Logic bám sát notebook 04_evaluate.ipynb.
"""

from pathlib import Path
from typing import Dict, Union

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def load_model(model_path: Union[str, Path]):
    """
    Nạp mô hình đã được đóng gói sẵn từ tệp joblib.

    Parameters:
    -----------
    model_path : str hoặc Path
        Đường dẫn tới file model.joblib.

    Returns:
    --------
    Pipeline
        Mô hình scikit-learn đã được nạp.
    """
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Không tìm thấy mô hình tại: {path}")
    return joblib.load(path)


def predict(model, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
    """
    Dự đoán chất lượng rượu vang cho tập dữ liệu X bằng mô hình đã nạp.

    Parameters:
    -----------
    model : Pipeline
        Mô hình scikit-learn đã huấn luyện.
    X : pd.DataFrame hoặc np.ndarray
        Dữ liệu đầu vào cần dự đoán.

    Returns:
    --------
    np.ndarray
        Mảng giá trị dự đoán.
    """
    return model.predict(X)


def calculate_mae(y_true, y_pred) -> float:
    """Tính Mean Absolute Error (MAE)."""
    return float(mean_absolute_error(y_true, y_pred))


def calculate_mse(y_true, y_pred) -> float:
    """Tính Mean Squared Error (MSE)."""
    return float(mean_squared_error(y_true, y_pred))


def calculate_rmse(y_true, y_pred) -> float:
    """Tính Root Mean Squared Error (RMSE)."""
    mse = mean_squared_error(y_true, y_pred)
    return float(np.sqrt(mse))


def calculate_r2(y_true, y_pred) -> float:
    """Tính hệ số xác định R² (R-squared)."""
    return float(r2_score(y_true, y_pred))


def evaluate_model(y_true, y_pred) -> Dict[str, float]:
    """
    Tính toán toàn diện các chỉ số đánh giá cho mô hình hồi quy:
    - MAE  : Sai số tuyệt đối trung bình
    - MSE  : Sai số toàn phương trung bình
    - RMSE : Căn bậc hai của sai số toàn phương trung bình
    - R2   : Hệ số xác định R-squared

    Parameters:
    -----------
    y_true : pd.Series hoặc np.ndarray
        Giá trị thực tế.
    y_pred : np.ndarray
        Giá trị dự đoán từ mô hình.

    Returns:
    --------
    Dict[str, float]
        Dictionary chứa các chỉ số đánh giá: {"MAE", "MSE", "RMSE", "R2"}.
    """
    return {
        "MAE": calculate_mae(y_true, y_pred),
        "MSE": calculate_mse(y_true, y_pred),
        "RMSE": calculate_rmse(y_true, y_pred),
        "R2": calculate_r2(y_true, y_pred),
    }


def print_evaluation_results(metrics: Dict[str, float]) -> None:
    """
    In kết quả đánh giá theo định dạng chuẩn hiển thị trong notebook 04_evaluate.ipynb.

    Parameters:
    -----------
    metrics : Dict[str, float]
        Dictionary chứa các chỉ số MAE, MSE, RMSE, R2.
    """
    try:
        print("===== KẾT QUẢ ĐÁNH GIÁ =====")
        print(f"MAE  : {metrics['MAE']:.6f}")
        print(f"MSE  : {metrics['MSE']:.6f}")
        print(f"RMSE : {metrics['RMSE']:.6f}")
        print(f"R²   : {metrics['R2']:.6f}")
    except UnicodeEncodeError:
        print("===== KET QUA DANH GIA =====")
        print(f"MAE  : {metrics['MAE']:.6f}")
        print(f"MSE  : {metrics['MSE']:.6f}")
        print(f"RMSE : {metrics['RMSE']:.6f}")
        print(f"R2   : {metrics['R2']:.6f}")


if __name__ == "__main__":
    try:
        print("--- Kiểm tra module evaluate ---")
        print("Các hàm đánh giá có sẵn:")
        print("- load_model(model_path)")
        print("- predict(model, X)")
        print("- calculate_mae(y_true, y_pred)")
        print("- calculate_mse(y_true, y_pred)")
        print("- calculate_rmse(y_true, y_pred)")
        print("- calculate_r2(y_true, y_pred)")
        print("- evaluate_model(y_true, y_pred)")
        print("- print_evaluation_results(metrics)")
        print("\nLưu ý: Không tự động chạy đánh giá hoặc tải model khi import module.")
    except UnicodeEncodeError:
        print("--- Kiem tra module evaluate ---")
        print("Cac ham danh gia co san:")
        print("- load_model(model_path)")
        print("- predict(model, X)")
        print("- calculate_mae(y_true, y_pred)")
        print("- calculate_mse(y_true, y_pred)")
        print("- calculate_rmse(y_true, y_pred)")
        print("- calculate_r2(y_true, y_pred)")
        print("- evaluate_model(y_true, y_pred)")
        print("- print_evaluation_results(metrics)")
        print("\nLuu y: Khong tu dong chay danh gia hoac tai model khi import module.")
