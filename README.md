# Dự đoán chất lượng rượu vang bằng hồi quy (Wine Quality Prediction using Regression)

> **Báo cáo đồ án môn học: Học máy cơ bản (Machine Learning)**

---

## 1. Thông tin chung

* **Đề tài:** Dự đoán chất lượng rượu vang bằng hồi quy (Wine Quality Prediction using Regression)
* **Thành viên thực hiện:**
  1. **Nguyễn Văn Vũ** – MSSV: `12523093`
  2. **Nguyễn Văn Linh** – MSSV: `10123207`
* **Hệ thống Git:**
  * Quản lý phiên bản mã nguồn với Git
  * Nhánh chính (default branch): `main`

---

## 2. Mô tả bài toán

* **Mục tiêu:** Dự đoán điểm chất lượng cảm quan của rượu vang đỏ dựa trên các thành phần hóa lý đo lường trong phòng thí nghiệm.
* **Đầu vào (Input):** Đúng 11 thuộc tính hóa lý (features) của mẫu rượu vang đỏ.
* **Đầu ra (Output):** Điểm chất lượng rượu `quality` (thang điểm đánh giá từ 3 đến 8).
* **Phân loại bài toán:** Bài toán **Hồi quy (Regression)** trong học máy có giám sát (Supervised Learning).

---

## 3. Dữ liệu (Dataset)

* **Tên dataset:** Red Wine Quality (`winequality-red.csv`)
* **Nguồn dữ liệu:** UCI Machine Learning Repository - Wine Quality Dataset (Cortez et al., 2009).
  * DOI: `10.24432/C56S3T`
  * Chi tiết tài liệu: xem tại [DATA.md](ai-models/data/DATA.md)
* **Đặc điểm dữ liệu:**
  * **Kích thước ban đầu:** 1599 dòng, 12 cột (11 features hóa lý + 1 target `quality`).
  * **Xử lý trùng lặp:** Sau khi loại bỏ 240 dòng trùng lặp (duplicates), dataset còn lại **1359 dòng**.
  * **Giá trị thiếu (Missing values):** Hoàn toàn không có giá trị thiếu (0 missing values) trong dữ liệu ban đầu.
  * **Biến mục tiêu (`quality`):** Giá trị số nguyên từ 3 đến 8 (phân bố tập trung ở điểm 5 và 6).
* **Lưu trữ dữ liệu:** Đóng gói lưu trữ tại [ai-models/data/dataset.zip](ai-models/data/dataset.zip).

---

## 4. Danh sách 11 thuộc tính đầu vào (Features)

Danh sách 11 thuộc tính hóa lý đầu vào được sắp xếp theo đúng thứ tự quy chuẩn trong toàn bộ pipeline và API:

1. `fixed acidity` (độ axit cố định)
2. `volatile acidity` (độ axit bay hơi)
3. `citric acid` (hàm lượng axit citric)
4. `residual sugar` (lượng đường dư)
5. `chlorides` (hàm lượng muối clorua)
6. `free sulfur dioxide` (lưu huỳnh điôxít tự do)
7. `total sulfur dioxide` (tổng lượng lưu huỳnh điôxít)
8. `density` (tỷ trọng)
9. `pH` (độ pH)
10. `sulphates` (hàm lượng sunfat)
11. `alcohol` (nồng độ cồn)

---

## 5. Quy trình Machine Learning

Quy trình phát triển mô hình được thực hiện tuần tự và nhất quán:

```text
Dataset (winequality-red.csv)
    ↓
EDA (Khám phá dữ liệu, vẽ biểu đồ phân phối và tương quan)
    ↓
Remove duplicates (1599 → 1359 dòng)
    ↓
Train/Test Split (80% train / 20% test, random_state=42)
    ↓
Pipeline Preprocessing: SimpleImputer(strategy="median") + StandardScaler()
    ↓
Train models (Linear Regression, Ridge, Random Forest, Gradient Boosting)
    ↓
Evaluate & So sánh mô hình trên tập Test
    ↓
Select Final Model (Random Forest Regressor Tuned)
    ↓
Package model.joblib (Tích hợp trọn gói Preprocessing + Model)
    ↓
AI Service (FastAPI :8000)
    ↓
Backend API (FastAPI :5000)
    ↓
Frontend (Nginx / Web :3000)
```

---

## 6. Phân tích khám phá dữ liệu (EDA)

Notebook phân tích được lưu tại [ai-models/colab/01_eda.ipynb](ai-models/colab/01_eda.ipynb). 
Các biểu đồ trực quan hóa được xuất lưu tại thư mục [docs/figures/](docs/figures/):

1. `01_quality_distribution.png`: Phân phối tần suất điểm chất lượng rượu vang.
2. `02_alcohol_distribution.png`: Phân phối nồng độ cồn trong các mẫu rượu.
3. `03_alcohol_vs_quality.png`: Tương quan giữa nồng độ cồn và chất lượng rượu.
4. `04_correlation_heatmap.png`: Ma trận hệ số tương quan giữa 11 thuộc tính và biến mục tiêu.
5. `05_volatile_acidity_vs_quality.png`: Mối tương quan âm giữa độ axit bay hơi và chất lượng rượu vang.

---

## 7. Tiền xử lý dữ liệu (Preprocessing)

Logic tiền xử lý đồng bộ giữa notebook [02_preprocess.ipynb](ai-models/colab/02_preprocess.ipynb) và mã nguồn [ai-models/src/preprocess.py](ai-models/src/preprocess.py):

* **Loại bỏ dữ liệu trùng lặp:** 1599 dòng ban đầu $\rightarrow$ còn **1359 dòng** hợp lệ.
* **Phân chia tập train/test:** Tỷ lệ **80% train / 20% test** (`test_size=0.2`), cố định `random_state=42` (tập train gồm 1087 mẫu, tập test gồm 272 mẫu).
* **Pipeline tiền xử lý chuẩn:**
  * `SimpleImputer(strategy="median")`: Dự phòng điền giá trị thiếu bằng trung vị nếu phát sinh trong tương lai.
  * `StandardScaler()`: Chuẩn hóa các đặc trưng dựa trên giá trị trung bình và độ lệch chuẩn, giúp dữ liệu có thang đo đồng nhất.

---

## 8. Huấn luyện mô hình (Training)

Thực hiện thử nghiệm và so sánh 4 thuật toán học máy:
1. **Linear Regression**
2. **Ridge Regression**
3. **Random Forest Regressor**
4. **Gradient Boosting Regressor**

### Bảng thử nghiệm và tinh chỉnh mô hình

| Mô hình | Siêu tham số chính | CV RMSE |
|---|---|---:|
| Ridge Regression | alpha = 10 | 0.664837 |
| Random Forest | n_estimators=200, max_depth=10, min_samples_split=2 | 0.658339 |
| Gradient Boosting | learning_rate=0.05, max_depth=3, n_estimators=100 | 0.657053 |

Các siêu tham số trên được xác định thông qua quá trình tìm kiếm tham số trong bước huấn luyện. Mô hình chính thức sau đó được đánh giá lại trên tập Test.

Trong các mô hình được thử nghiệm, Random Forest Regressor Tuned được lựa chọn làm mô hình chính thức dựa trên kết quả đánh giá trên tập Test, với RMSE = 0.616043 và R² = 0.464240.

---

## 9. Mô hình chính thức (Final Model)

* **Thuật toán:** Random Forest Regressor (Tuned)
* **Bộ siêu tham số tối ưu:**
  * `n_estimators = 200`
  * `max_depth = 10`
  * `min_samples_split = 2`
  * `random_state = 42`

---

## 10. Đánh giá mô hình (Evaluation)

Kết quả đánh giá chính thức của mô hình Random Forest Regressor Tuned trên tập kiểm thử (Test Set 80/20) khớp tuyệt đối giữa [04_evaluate.ipynb](ai-models/colab/04_evaluate.ipynb), [evaluate.py](ai-models/src/evaluate.py) và [metadata.json](ai-models/models/metadata.json):

| Chỉ số đánh giá | Giá trị chính thức |
| :--- | :---: |
| **MAE** (Mean Absolute Error) | **0.468880** |
| **MSE** (Mean Squared Error) | **0.379509** |
| **RMSE** (Root Mean Squared Error) | **0.616043** |
| **R²** (R-squared Score) | **0.464240** |

---

## 11. Đóng gói mô hình (Model Packaging)

Các tệp đóng gói được lưu trữ tại [ai-models/models/](ai-models/models/):

* `model.joblib`: Đóng gói một `Pipeline` scikit-learn duy nhất, bao gồm bước tiền xử lý (`SimpleImputer` + `StandardScaler`) và mô hình đã huấn luyện (`RandomForestRegressor`). Nhờ vậy khi inference, dữ liệu chỉ cần truyền trực tiếp vào pipeline mà không cần tiền xử lý rời rạc bên ngoài.
* `schema.json`: Định nghĩa kiểu dữ liệu (`float64`), ngưỡng min/max và thứ tự chính xác của 11 thuộc tính đầu vào.
* `metadata.json`: Lưu trữ thông tin chi tiết về phiên bản mô hình, siêu tham số, kích thước dataset, phiên bản thư viện và chỉ số đo lường chính thức.

---

## 12. Kiến trúc hệ thống

```text
       Người dùng / Trình duyệt Web
                   ↓ (Port 3000)
      Frontend Web (Nginx / Vanilla JS)
                   ↓ HTTP POST /predict (Port 5000)
         Backend API (FastAPI)
                   ↓ HTTP POST /predict (Port 8000)
          AI Service (FastAPI)
                   ↓
         Pipeline (model.joblib)
                   ↓
         Điểm chất lượng rượu (quality)
```

* **Frontend:** Chạy qua Web server (Nginx trong Docker) trên cổng `3000`.
* **Backend API:** FastAPI chạy trên cổng `5000`, làm nhiệm vụ nhận request từ Frontend, validate dữ liệu và chuyển tiếp (forward) sang AI Service.
* **AI Service:** FastAPI chạy trên cổng `8000`, nạp `model.joblib` và trực tiếp thực thi dự đoán.
* **Kết nối trong mạng Docker (Docker Network):** Backend kết nối tới AI Service qua URL nội bộ `http://ai-service:8000`.

---

## 13. Danh sách API Endpoints

### AI Service (Port 8000)
* `GET /health`: Kiểm tra sức khỏe dịch vụ (trả về `{"status": "ok"}`).
* `GET /`: Trang chủ AI Service, hiển thị trạng thái nạp mô hình.
* `POST /predict`: Nhận 11 thuộc tính hóa lý (JSON body), trả về điểm chất lượng dự đoán (`{"prediction": ...}`).

### Backend API (Port 5000)
* `GET /health`: Kiểm tra tình trạng Backend (trả về `{"status": "ok"}`).
* `GET /`: Trang chủ thông tin Backend và địa chỉ `ai_service_url` đang kết nối.
* `POST /predict`: Tiếp nhận 11 thuộc tính từ Client/Frontend, validate và chuyển tiếp tới AI Service.

---

## 14. Kiểm thử tự động (Testing)

Dự án có sẵn các bộ kiểm thử tự động (Unit/Integration Test) bằng `pytest` và `FastAPI TestClient`:

* **AI Service Test Suite ([ai-models/service/test_api.py](ai-models/service/test_api.py)):** **Đạt 6/6 tests**
  * `test_root`: Kiểm tra GET /
  * `test_health`: Kiểm tra GET /health
  * `test_predict_missing_feature`: Chặn request thiếu feature (422)
  * `test_predict_invalid_data_type`: Chặn request sai kiểu dữ liệu (422)
  * `test_predict_extra_feature`: Chặn request thừa feature lạ (422)
  * `test_predict_model_status`: Kiểm tra phản hồi dự đoán hợp lệ khi có model.joblib
* **Backend API Test Suite ([app/backend/test_api.py](app/backend/test_api.py)):** **Đạt 7/7 tests**
  * `test_root`: Kiểm tra GET /
  * `test_health`: Kiểm tra GET /health
  * `test_predict_success_mock`: Chuyển tiếp kết quả dự đoán thành công
  * `test_predict_missing_feature`: Validate thiếu feature (422)
  * `test_predict_invalid_data_type`: Validate sai kiểu dữ liệu (422)
  * `test_predict_extra_feature`: Validate thừa feature lạ (422)
  * `test_predict_ai_service_unavailable`: Xử lý ngoại lệ khi AI Service ngừng hoạt động (503)

👉 **Tổng cộng: 13/13 test cases đều đạt chuẩn (PASS).**

---

## 15. Hướng dẫn khởi chạy hệ thống

### Cách 1: Khởi chạy toàn bộ hệ thống bằng Docker Compose (Khuyến nghị)

Khởi động đồng thời cả 3 dịch vụ (`ai-service`, `backend`, `frontend`) chỉ với 1 câu lệnh từ thư mục gốc project:

```bash
docker compose -p winequality up -d --build
```

Sau khi khởi chạy thành công, truy cập các dịch vụ:
* **Giao diện người dùng (Frontend):** [http://localhost:3000](http://localhost:3000)
* **Backend API Documentation:** [http://localhost:5000/docs](http://localhost:5000/docs)
* **AI Service Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Kiểm tra trạng thái AI Service:** [http://localhost:8000/health](http://localhost:8000/health)

Để dừng toàn bộ hệ thống:
```bash
docker compose -p winequality down
```

> **Ghi chú về môi trường Windows:** Dự án đã được thiết kế và kiểm thử E2E đầy đủ bằng Docker Compose. Trong môi trường Windows, nếu đường dẫn thư mục project chứa ký tự Unicode có dấu hoặc nằm trong thư mục đồng bộ OneDrive, khi tương tác qua Git Bash CLI nên thêm tiền tố `MSYS_NO_PATHCONV=1` (ví dụ: `MSYS_NO_PATHCONV=1 docker compose -p winequality up -d --build`) để tránh việc Git Bash tự ý chuyển đổi đường dẫn.

---

### Cách 2: Khởi chạy riêng lẻ từng dịch vụ (Chế độ Local)

Nếu muốn chạy trực tiếp bằng môi trường Python trên máy:

1. **Khởi chạy AI Service (Cửa sổ Terminal 1):**
   ```bash
   pip install -r ai-models/service/requirements.txt
   python -m uvicorn main:app --port 8000 --app-dir ai-models/service
   ```
   *Kiểm tra tại:* [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

2. **Khởi chạy Backend API (Cửa sổ Terminal 2):**
   ```bash
   pip install -r app/backend/requirements.txt
   python -m uvicorn main:app --port 5000 --app-dir app/backend
   ```
   *Kiểm tra tại:* [http://127.0.0.1:5000/health](http://127.0.0.1:5000/health)

3. **Mở Frontend (Cửa sổ Terminal 3 hoặc trình duyệt):**
   * *Cách A:* Nhấp đúp chuột trực tiếp vào tệp `app/frontend/index.html`.
   * *Cách B:* Chạy máy chủ tĩnh:
     ```bash
     python -m http.server 3000 --directory app/frontend
     ```
     Truy cập tại: [http://127.0.0.1:3000](http://127.0.0.1:3000)

---

## 16. Cấu trúc thư mục dự án

```text
.
├── app/
│   ├── frontend/                  # Mã nguồn giao diện Web (HTML, CSS, JS)
│   │   ├── index.html
│   │   ├── style.css
│   │   ├── script.js
│   │   └── README.md
│   └── backend/                   # FastAPI Backend chuyển tiếp yêu cầu
│       ├── main.py
│       ├── schemas.py
│       ├── requirements.txt
│       ├── test_api.py
│       ├── Dockerfile
│       └── .env.example
├── ai-models/
│   ├── colab/                     # Các notebook phân tích và huấn luyện
│   │   ├── 01_eda.ipynb
│   │   ├── 02_preprocess.ipynb
│   │   ├── 03_train.ipynb
│   │   ├── 04_evaluate.ipynb
│   │   └── README.md
│   ├── data/                      # Dữ liệu nguồn và tài liệu mô tả
│   │   ├── dataset.zip
│   │   └── DATA.md
│   ├── models/                    # Tệp mô hình và metadata đã đóng gói
│   │   ├── model.joblib
│   │   ├── schema.json
│   │   ├── metadata.json
│   │   └── README.md
│   ├── service/                   # FastAPI AI Service phục vụ dự đoán
│   │   ├── main.py
│   │   ├── schemas.py
│   │   ├── requirements.txt
│   │   ├── requirements-dev.txt
│   │   ├── test_api.py
│   │   └── Dockerfile
│   ├── src/                       # Module mã nguồn Python tái sử dụng
│   │   ├── preprocess.py
│   │   ├── train.py
│   │   └── evaluate.py
│   └── requirements.txt
├── docs/
│   └── figures/                   # Biểu đồ EDA và so sánh mô hình
├── docker-compose.yml             # Cấu hình khởi chạy trọn gói Docker Compose
├── .env.example                   # Tệp mẫu biến môi trường
├── .gitignore                     # Cấu hình bỏ qua các tệp không cần thiết
└── README.md                      # Báo cáo tổng quan dự án
```

---

## 17. Biến môi trường và Bảo mật (Environment & Security)

* Tệp cấu hình chứa giá trị nhạy cảm `.env` đã được đưa vào `.gitignore` và **tuyệt đối không commit** lên Git.
* Dự án cung cấp mẫu `.env.example` để người dùng dễ dàng cấu hình môi trường khi triển khai.
* Mã nguồn không chứa bất kỳ API key, token, mật khẩu thật hay tệp thông tin xác thực (`kaggle.json`).
