# Thai OCR Service (PaddleOCR)

Backend service สำหรับอ่านข้อความภาษาไทยจากภาพสลิป โดยใช้ PaddleOCR

## การติดตั้ง

1. สร้าง virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # สำหรับ macOS/Linux
# หรือ
venv\Scripts\activate  # สำหรับ Windows
```

2. ติดตั้ง dependencies:
```bash
pip install -r requirements.txt
```

## การรัน Service

```bash
python app.py
```

Service จะรันที่ `http://localhost:5000`

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
- image: (file) รูปภาพที่ต้องการ OCR

หรือ

POST /ocr
Content-Type: application/json

{
  "image_base64": "base64_encoded_image_string"
}
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

## การ Deploy

### สำหรับ Production (แนะนำใช้ Gunicorn):

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### สำหรับ Docker:

สร้าง `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build และ run:
```bash
docker build -t thai-ocr-service .
docker run -p 5000:5000 thai-ocr-service
```

## การตั้งค่าใน Flutter App

หลังจาก deploy service แล้ว ต้องตั้งค่า URL ใน Flutter app:

1. เปิดแอป Flutter
2. ไปที่ Settings (ถ้ามี) หรือแก้ไขใน code:
   - ใช้ `SharedPreferences` เพื่อเก็บ OCR service URL
   - Key: `ocr_service_url`
   - Default: `http://localhost:5000` (สำหรับ development)
   - Production: ตั้งเป็น URL ของ server ที่ deploy แล้ว (เช่น `https://your-ocr-service.com`)

ตัวอย่างการตั้งค่าใน code:
```dart
final prefs = await SharedPreferences.getInstance();
await prefs.setString('ocr_service_url', 'https://your-ocr-service.com');
```

## หมายเหตุ

- PaddleOCR จะดาวน์โหลดโมเดลภาษาไทยอัตโนมัติครั้งแรกที่รัน (ประมาณ 10-20 MB)
- สำหรับการใช้งานจริง ควร deploy บน cloud service เช่น Heroku, AWS, Google Cloud, หรือ Railway
- ตั้งค่า CORS ให้รองรับ domain ของแอป Flutter
- สำหรับ development บน Android Emulator: ใช้ `http://10.0.2.2:5000` แทน `localhost:5000`
- สำหรับ development บน iOS Simulator: ใช้ `http://localhost:5000` ได้เลย
- สำหรับ device จริง: ต้องใช้ IP address ของเครื่องที่รัน service (เช่น `http://192.168.1.100:5000`)

