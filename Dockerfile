FROM python:3.9-slim

WORKDIR /app

# ลดขนาด image
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libsm6 libxext6 libxrender1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# IMPORTANT: ใช้ sh -c เพื่อให้ $PORT ถูกแทนค่า
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT}"
