# Sử dụng Python 3.11-slim chính thức
FROM python:3.11-slim

# Thiết lập các biến môi trường Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Thiết lập thư mục làm việc gốc trong container
WORKDIR /app

# Sao chép requirements.txt của Backend
COPY app/backend/requirements.txt /app/requirements.txt

# Cài đặt dependencies bằng pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Sao chép mã nguồn của Backend (chỉ main.py và schemas.py, không copy __pycache__)
COPY app/backend/main.py /app/main.py
COPY app/backend/schemas.py /app/schemas.py

# Mở cổng 5000
EXPOSE 5000

# Khởi chạy dịch vụ FastAPI Backend bằng uvicorn trên cổng 5000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
