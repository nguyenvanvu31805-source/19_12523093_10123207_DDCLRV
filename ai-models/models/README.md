# AI Models Storage

Thư mục này lưu trữ các tệp mô hình đã đóng gói từ Google Colab:

- `model.joblib`: Pipeline đóng gói hoàn chỉnh (SimpleImputer + StandardScaler + RandomForestRegressor tuned).
- `schema.json`: Cấu hình schema 11 features đầu vào.
- `metadata.json`: Thông tin huấn luyện, tham số siêu tham số và chỉ số đánh giá (MAE, MSE, RMSE, R2).

## Hướng dẫn
Vui lòng sao chép 3 tệp `model.joblib`, `schema.json` và `metadata.json` đã tải về từ Google Colab vào đúng thư mục này.
AI Service tại `ai-models/service/` sẽ tự động nhận diện và nạp mô hình từ đường dẫn:
`../models/model.joblib`
`../models/schema.json`
