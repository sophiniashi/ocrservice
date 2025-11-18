#!/bin/bash
# Script สำหรับรัน OCR Service

echo "Starting Thai OCR Service (PaddleOCR)..."

# ตรวจสอบว่ามี virtual environment หรือไม่
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# ติดตั้ง dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# รัน service
echo "Starting service on http://0.0.0.0:5000"
python app.py

