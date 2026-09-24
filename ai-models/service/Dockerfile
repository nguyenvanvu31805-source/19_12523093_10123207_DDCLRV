# Sử dụng Python 3.11-slim chính thức
FROM python:3.11-slim

# Thiết lập biến môi trường Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Thiết lập thư mục làm việc gốc trong container
WORKDIR /app

# Sao chép và cài đặt các thư viện phụ thuộc production của AI Service từ PyPI
COPY ai-models/service/requirements.txt /app/service/requirements.txt
RUN pip install --no-cache-dir --default-timeout=1000 -r /app/service/requirements.txt

# Sao chép các tệp mô hình và metadata chính thức
COPY ai-models/models/model.joblib /app/models/model.joblib
COPY ai-models/models/schema.json /app/models/schema.json
COPY ai-models/models/metadata.json /app/models/metadata.json

# Sao chép mã nguồn của AI Service
COPY ai-models/service/ /app/service/

# Chuyển thư mục làm việc vào service để uvicorn nạp đúng main:app
# và Path(__file__).resolve().parent.parent / "models" trỏ chính xác về /app/models
WORKDIR /app/service

# Mở cổng 8000
EXPOSE 8000

# Khởi chạy dịch vụ FastAPI bằng uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
