# Thai OCR Service

OCR Service สำหรับอ่านสลิปโอนเงินภาษาไทย โดยใช้ PaddleOCR

## Features

- อ่านข้อความภาษาไทยจากภาพสลิปโอนเงิน
- รองรับ PP-OCR Lite model (ขนาดเล็ก)
- Lazy loading เพื่อลด memory usage
- RESTful API ด้วย FastAPI

## API Endpoints

### Health Check
```
GET /health
```

### OCR Processing
```
POST /ocr
Content-Type: multipart/form-data

Form data:
- file: (image file) รูปภาพสลิปที่ต้องการ OCR
```

Response:
```json
{
  "text": "ข้อความที่อ่านได้",
  "lines": 10,
  "characters": 150,
  "success": true
}
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --host 0.0.0.0 --port 5000
```

## Railway Deployment

Service จะ deploy อัตโนมัติเมื่อ push ไปยัง repository

Railway จะ:
- Build Docker image จาก Dockerfile
- Set PORT environment variable อัตโนมัติ
- Start service ด้วย uvicorn

## Example Usage

```bash
# Test health check
curl http://localhost:5000/health

# Test OCR
curl -X POST http://localhost:5000/ocr \
  -F "file=@slip.jpg"
```
