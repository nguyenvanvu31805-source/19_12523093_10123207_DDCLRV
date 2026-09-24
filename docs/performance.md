# Báo cáo Kiểm thử Hiệu năng (Performance / Load Test)

> **Dự án:** Dự đoán chất lượng rượu vang bằng hồi quy (Wine Quality Prediction using Regression)  
> **Thành viên:** Nguyễn Văn Vũ (12523093) – Nguyễn Văn Linh (10123207)  
> **Thời gian thực hiện:** 2026-09-25

---

## 1. Môi trường kiểm thử (Environment)

* **Hạ tầng triển khai:** Docker Compose v2 với 4 containers độc lập:
  * `wine-mongodb` (Mongo 7.0 - Cổng `27017`)
  * `wine-ai-service` (FastAPI + Scikit-Learn Model Pipeline - Cổng `8000`)
  * `wine-backend` (FastAPI Trung gian + MongoDB Client - Cổng `5000`)
  * `wine-frontend` (Nginx Web Server - Cổng `3000`)
* **Endpoint kiểm thử:** `POST http://127.0.0.1:5000/api/predict`
  * Luồng xử lý trọn gói thực tế: `Client/Frontend → Backend API → AI Service → MongoDB History → Client`
* **Thông tin phần cứng & hệ điều hành:**
  * **Hệ điều hành:** Windows 11 (64-bit)
  * **Bộ vi xử lý (CPU):** Intel64 Family 6 Model 154 Stepping 3 (GenuineIntel)
  * **Bộ nhớ RAM:** 16 GB (15.71 GB khả dụng)
* **Thông tin mô hình AI:**
  * **Model:** Random Forest Regressor (Tuned)
  * **Model Version:** 1.0.0
  * **Đóng gói:** Pipeline tích hợp tiền xử lý `SimpleImputer` + `StandardScaler` trong `model.joblib`

---

## 2. Giai đoạn Warm-up

Trước khi tiến hành đo lường hiệu năng chính thức, hệ thống được gửi các request warm-up để:
* Kích hoạt và nạp model `model.joblib` vào bộ nhớ RAM của container `wine-ai-service`.
* Khởi tạo pool kết nối mạng giữa Backend và AI Service (`httpx.AsyncClient`).
* Khởi tạo kết nối lazy initialization tới cơ sở dữ liệu MongoDB (`pymongo.MongoClient`).

> **Lưu ý quan trọng:** Toàn bộ request trong giai đoạn warm-up **HOÀN TOÀN KHÔNG** được tính vào kết quả benchmark chính thức.
* **Warm-up Kịch bản 1 (10 users):** 20 requests thành công (20/20 PASS).
* **Warm-up Kịch bản 2 (20 users):** 10 requests thành công (10/10 PASS).

---

## 3. Kịch bản kiểm thử (Test Scenarios)

* **Công cụ kiểm thử:** Script kiểm thử bất đồng bộ độc lập viết bằng Python (`asyncio` + `httpx`), lưu tại [scripts/load_test/load_test.py](../scripts/load_test/load_test.py).
* **Mỗi request:** Sinh một định danh duy nhất `X-Request-ID` (UUID) và gửi qua HTTP header.
* **Payload kiểm thử:** Đúng 11 thuộc tính hóa lý chuẩn của rượu vang đỏ:
  ```json
  {
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
  ```

---

## 4. Kết quả kiểm thử thực tế (Benchmark Results)

### Bảng tổng hợp đối chiếu với tiêu chí đánh giá

| Tiêu chí / Metric | Kịch bản 1 (10 Users) | Kịch bản 2 (20 Users) | Mục tiêu (Target) | Đánh giá |
|:---|---:|---:|---:|:---:|
| **Concurrency (Số user đồng thời)** | 10 | 20 | 10–20 concurrent users | **ĐẠT** |
| **Duration thực tế (Thời gian chạy)** | 60.13 s | 60.34 s | ~ 60 giây (1 phút) | **ĐẠT** |
| **Tổng số requests (Total)** | 1,862 | 1,773 | - | - |
| **Số requests thành công (Success)** | 1,862 | 1,773 | - | - |
| **Số requests lỗi (Errors / Failed)** | 0 | 0 | - | - |
| **Tỷ lệ lỗi (Error Rate)** | **0.00 %** | **0.00 %** | **< 1.0 %** | **ĐẠT XUẤT SẮC** |
| **Thông lượng (Throughput)** | **30.96 req/s** | **29.39 req/s** | - | **Rất cao** |
| **Độ trễ p50 (p50 Latency)** | **310.55 ms** (0.311 s) | **626.88 ms** (0.627 s) | - | **Rất nhanh** |
| **Độ trễ p90 (p90 Latency)** | **400.80 ms** (0.401 s) | **811.89 ms** (0.812 s) | - | - |
| **Độ trễ p95 (p95 Latency)** | **425.73 ms** (0.426 s) | **851.71 ms** (0.852 s) | **< 2.0 s (2000 ms)** | **ĐẠT XUẤT SẮC** |
| **Độ trễ p99 (p99 Latency)** | **496.22 ms** (0.496 s) | **1242.59 ms** (1.243 s) | - | - |
| **Độ trễ Min / Mean / Max** | 68.7 / 313.4 / 3343.7 ms | 117.7 / 641.5 / 6422.9 ms | - | - |

---

## 5. Truy vết Request Tracing (`X-Request-ID`)

Trong suốt quá trình load test, mỗi request gửi lên đều mang một header `X-Request-ID` độc nhất. Nhật ký ghi log từ Docker Compose xác nhận cơ chế tracing hoạt động xuyên suốt qua cả Backend và AI Service:

### Mẫu log thực tế từ container `wine-backend`:
```log
wine-backend  | 2026-09-24 18:47:56,606 - INFO - request_id=load-3-c4a9cc9561f2 method=POST path=/api/predict status=200 duration_ms=723.57
wine-backend  | 2026-09-24 18:47:56,611 - INFO - Đã lưu lịch sử dự đoán vào MongoDB thành công
wine-backend  | 2026-09-24 18:47:56,898 - INFO - request_id=load-12-110e53288b1b method=POST path=/api/predict status=200 duration_ms=374.18
wine-backend  | 2026-09-24 18:47:56,899 - INFO - Đã lưu lịch sử dự đoán vào MongoDB thành công
```

### Mẫu log thực tế tương ứng từ container `wine-ai-service`:
```log
wine-ai-service  | 2026-09-24 18:47:56,608 - INFO - request_id=load-12-110e53288b1b method=POST path=/predict status=start
wine-ai-service  | 2026-09-24 18:47:56,866 - INFO - request_id=load-12-110e53288b1b prediction=5.0947
wine-ai-service  | 2026-09-24 18:47:56,885 - INFO - request_id=load-12-110e53288b1b method=POST path=/predict status=200 duration_ms=277.17
```

---

## 6. Kiểm tra cơ sở dữ liệu MongoDB sau Load Test

* Sau khi hoàn tất 2 kịch bản kiểm thử tải, endpoint `GET http://127.0.0.1:5000/api/history?limit=10` được gọi để kiểm tra tính toàn vẹn của dữ liệu:
  * **HTTP Status Code:** `200 OK`
  * **Cấu trúc JSON:** Chuẩn schema `{"items": [...], "count": 10}`.
  * **Dữ liệu mẫu mới nhất:**
    ```json
    {
      "timestamp": "2026-09-24T18:47:56.900235+00:00",
      "input": {
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
      },
      "prediction": 5.0947
    }
    ```
* **Tổng số bản ghi đã lưu vào MongoDB:** **3,816 bản ghi**, xác nhận hệ thống ghi nhận toàn bộ các dự đoán mà không làm nghẽn hoặc sập MongoDB.

---

## 7. Kiểm tra độ ổn định & Test Suite sau Load Test

1. **Health Check:**
   * Backend: `GET http://127.0.0.1:5000/health` $\rightarrow$ `HTTP 200 {"status": "ok"}`
   * AI Service: `GET http://127.0.0.1:8000/health` $\rightarrow$ `HTTP 200 {"status": "ok"}`
2. **Kiểm thử hồi quy tự động (Regression Tests):**
   * **AI Service:** `10/10 tests PASS`
   * **Backend API:** `14/14 tests PASS`
   * **Tổng cộng:** `24/24 tests PASS (100%)`

---

## 8. Kết luận (Conclusion)

Dựa trên dữ liệu kiểm thử thực tế thu thập từ cả hai kịch bản:
1. **Error Rate:** Đạt **0.00%** ở cả mức 10 và 20 concurrent users (vượt xa yêu cầu `< 1%`).
2. **p95 Latency:** Đạt **425.73 ms** (với 10 users) và **851.71 ms** (với 20 users), thấp hơn rất nhiều so với ngưỡng quy định của giảng viên (**< 2.0 s / 2000 ms**).
3. **Throughput:** Duy trì ổn định ở mức xấp xỉ **30 requests/giây**, đáp ứng tốt nhu cầu phục vụ người dùng thực tế.
4. Hệ thống microservices (Frontend, Backend, AI Service, MongoDB) vận hành ổn định, không rò rỉ bộ nhớ, không rớt kết nối và bảo đảm khả năng truy vết hoàn chỉnh qua `X-Request-ID`.
