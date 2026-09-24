# DATASET

## 1. Tên dataset
Red Wine Quality

## 2. Nguồn dữ liệu
- **Nguồn chính thức**: UCI Machine Learning Repository - Wine Quality Dataset
- **URL**: https://archive.ics.uci.edu/dataset/186/wine+quality
- **DOI**: https://doi.org/10.24432/C56S3T

## 3. Tác giả dataset
- Cortez, P., Cerdeira, A., Almeida, F., Matos, T., & Reis, J. (2009). *Modeling wine preferences by data mining from physicochemical properties*. Decision Support Systems, Elsevier, 47(4):547-553. ISSN: 0167-9236.

## 4. Giấy phép
- Creative Commons Attribution 4.0 International (CC BY 4.0).
- Dataset được sử dụng cho mục đích học tập và nghiên cứu trong phạm vi đồ án môn học.

## 5. File dữ liệu
- File dữ liệu: `winequality-red.csv`
- Đóng gói lưu trữ tại: `ai-models/data/dataset.zip` (bên trong chứa duy nhất file `winequality-red.csv`).
- Mô tả: Mẫu rượu vang đỏ Vinho Verde từ miền Bắc Bồ Đào Nha.

## 6. Bài toán
- **Bài toán**: Hồi quy (Regression) - Dự đoán chất lượng rượu vang.
- **Biến mục tiêu (Target)**: `quality`
  - Điểm chất lượng cảm quan của rượu vang đỏ.
  - Giá trị `quality` nằm trong khoảng từ **3 đến 8** (các giá trị nguyên: 3, 4, 5, 6, 7, 8).

## 7. Các thuộc tính đầu vào (11 Features)
Danh sách 11 thuộc tính hóa lý đầu vào theo đúng thứ tự:
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

## 8. Đặc điểm dữ liệu ban đầu
- **Số dòng ban đầu**: 1599 dòng.
- **Số cột**: 12 cột (11 thuộc tính đầu vào + 1 biến mục tiêu).
- **Kiểu dữ liệu**:
  - 11 thuộc tính đầu vào: số thực (`float64`).
  - Target `quality`: số nguyên (`int64`).
- **Giá trị thiếu (Missing values)**: Hoàn toàn không có giá trị thiếu (0 missing values).
- **Phạm vi giá trị target**: Điểm `quality` có giá trị từ 3 đến 8.

## 9. Tiền xử lý dữ liệu (Data Preprocessing)
Các bước tiền xử lý đã áp dụng theo đúng quy trình:
- **Xử lý trùng lặp (Duplicate)**: 
  - Duplicate được phát hiện và loại bỏ trước khi huấn luyện (`df.drop_duplicates().reset_index(drop=True)`).
  - Số dòng dữ liệu sau khi loại bỏ trùng lặp: **1359 dòng** (loại bỏ 240 dòng trùng).
- **Xử lý ngoại lai (Outliers)**: Không xóa outlier để giữ toàn vẹn thông tin các mẫu rượu vang đặc biệt.
- **Tách dữ liệu**: Tách thành ma trận biến đầu vào $X$ (11 features) và biến mục tiêu $y$ (`quality`).
- **Phân chia tập train/test**:
  - Tỷ lệ: 80% train / 20% test.
  - `random_state = 42`.
  - Số lượng mẫu tập huấn luyện (train): **1087 dòng**.
  - Số lượng mẫu tập kiểm thử (test): **272 dòng**.
- **Pipeline tiền xử lý**:
  - `SimpleImputer(strategy="median")`: Điền khuyết tật dữ liệu bằng trung vị nếu phát sinh giá trị thiếu trong tương lai.
  - `StandardScaler()`: Chuẩn hóa dữ liệu về phân phối chuẩn chuẩn tắc (trung bình 0, độ lệch chuẩn 1).

## 10. Trích dẫn
```bibtex
@misc{misc_wine_quality_186,
  author       = {Cortez, Paulo, Cerdeira, António, Almeida, Fernando, Matos, Telmo, and Reis, José},
  title        = {{Wine Quality}},
  year         = {2009},
  howpublished = {UCI Machine Learning Repository},
  note         = {{DOI}: https://doi.org/10.24432/C56S3T}
}
```