# Wine Quality Prediction - Frontend Web

Giao diện web người dùng cho đồ án Machine Learning: **Dự đoán chất lượng rượu vang bằng hồi quy (Red Wine Quality Regression)**.

---

## 1. Công nghệ sử dụng
- **HTML5 / CSS3 / JavaScript thuần (Vanilla JS)**: Giao diện nhẹ, responsive, không yêu cầu cài đặt thêm node_modules hay framework phức tạp.
- **Giao thức kết nối**: Gọi REST API tới Backend qua HTTP `POST /predict`.

---

## 2. Kiến trúc luồng dữ liệu
```text
Người dùng nhập liệu trên Web
         ↓ (HTTP POST :5000/predict)
Backend FastAPI (app/backend/main.py)
         ↓ (HTTP POST :8000/predict)
AI Service (ai-models/service/main.py)
         ↓
Pipeline Model (model.joblib)
         ↓
Trả về điểm chất lượng dự đoán (quality score)
```

---

## 3. Hướng dẫn khởi chạy

### Bước 1: Khởi động AI Service
Mở terminal 1:
```bash
python -m uvicorn main:app --port 8000 --app-dir ai-models/service
```

### Bước 2: Khởi động Backend
Mở terminal 2:
```bash
python -m uvicorn main:app --port 5000 --app-dir app/backend
```

### Bước 3: Mở Frontend
Có 2 cách:
- **Cách 1 (Đơn giản nhất)**: Nhấp đúp chuột trực tiếp vào file `app/frontend/index.html` để mở trên trình duyệt web bất kỳ.
- **Cách 2 (Sử dụng máy chủ HTTP cục bộ qua Python)**:
  Mở terminal 3:
  ```bash
  python -m http.server 3000 --directory app/frontend
  ```
  Sau đó mở trình duyệt truy cập: [http://127.0.0.1:3000](http://127.0.0.1:3000)

---

## 4. Chức năng chính
- Form nhập đầy đủ **11 thuộc tính hóa lý** của rượu vang theo đúng chuẩn dataset UCI.
- Nút **"Điền giá trị mẫu"**: Điền nhanh bộ thông số chuẩn (Fixed acidity=7.4, Volatile acidity=0.7, Citric acid=0.0, Residual sugar=1.9, Chlorides=0.076, Free SO2=11, Total SO2=34, Density=0.9978, pH=3.51, Sulphates=0.56, Alcohol=9.4).
- Nút **"Dự đoán chất lượng"**: Gửi dữ liệu tới Backend, hiển thị trạng thái `Đang dự đoán...`, và hiển thị điểm số dự đoán chính xác khi hoàn thành.
- Xử lý lỗi trực quan: Tự động phát hiện và hiển thị thông báo khi không kết nối được Backend, khi dữ liệu nhập không hợp lệ (HTTP 422), hoặc khi AI Service chưa sẵn sàng (HTTP 503).
