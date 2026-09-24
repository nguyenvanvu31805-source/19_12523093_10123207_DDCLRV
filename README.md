# Wine Quality Regression

Đồ án Machine Learning: **Dự đoán chất lượng rượu vang đỏ bằng phương pháp hồi quy (Regression)**.

## 1. Cấu trúc dự án

```text
WineQualityRegression/
├── app/
│   ├── frontend/
│   └── backend/
│
├── ai-models/
│   ├── colab/
│   │   ├── 01_eda.ipynb
│   │   ├── 02_preprocess.ipynb
│   │   ├── 03_train.ipynb
│   │   └── 04_evaluate.ipynb
│   │
│   ├── src/
│   ├── data/
│   │   ├── dataset.zip
│   │   └── DATA.md
│   │
│   ├── models/
│   │   ├── model.joblib
│   │   ├── schema.json
│   │   └── metadata.json
│   │
│   ├── service/
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── requirements.txt
│   │   └── test_api.py
│   └── requirements.txt
│
├── docs/
│   └── figures/
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## 2. Thông tin mô hình
- **Thuật toán:** Random Forest Regressor (đã tinh chỉnh siêu tham số)
- **Pipeline:** `SimpleImputer(strategy="median")` -> `StandardScaler()` -> `RandomForestRegressor(n_estimators=200, max_depth=10, min_samples_split=2, random_state=42)`
- **Kết quả đánh giá trên tập Test (80/20):**
  - MAE = 0.468880
  - MSE = 0.379509
  - RMSE = 0.616043
  - R2 = 0.464240

## 3. Khởi chạy AI Service (Giai đoạn 5.2)

1. Cài đặt thư viện:
   ```bash
   pip install -r ai-models/service/requirements.txt
   ```

2. Đảm bảo đã chép `model.joblib`, `schema.json`, `metadata.json` từ Google Colab vào thư mục `ai-models/models/`.

3. Khởi chạy server:
   ```bash
   cd ai-models/service
   uvicorn main:app --reload
   ```

4. Truy cập tài liệu API tương tác tại:
   `http://127.0.0.1:8000/docs`
