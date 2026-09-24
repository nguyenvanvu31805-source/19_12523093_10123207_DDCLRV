# Google Colab Notebooks

Thư mục này lưu trữ các Jupyter Notebooks phát triển trên Google Colab:

- `01_eda.ipynb`: Phân tích khám phá dữ liệu (EDA), phân phối biến, tương quan, phát hiện outliers.
- `02_preprocess.ipynb`: Tiền xử lý dữ liệu, loại bỏ duplicates (1599 -> 1359 dòng), xử lý missing values, chuẩn hóa.
- `03_train.ipynb`: Huấn luyện mô hình, tinh chỉnh siêu tham số Random Forest Regressor (n_estimators=200, max_depth=10, min_samples_split=2).
- `04_evaluate.ipynb`: Đánh giá mô hình trên tập test (MAE=0.468880, MSE=0.379509, RMSE=0.616043, R2=0.464240) và xuất file `model.joblib`, `schema.json`, `metadata.json`.
