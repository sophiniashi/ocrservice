from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
from PIL import Image
import io
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Thai OCR Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ocr = None

def get_ocr():
    global ocr
    if ocr is None:
        logger.info("Initializing PaddleOCR (latin multi-language, supports Thai)...")
        ocr = PaddleOCR(
            # ใช้โมเดล 'latin' ที่รองรับตัวอักษรยุโรปและหลายภาษา รวมถึงไทย
            # (เวอร์ชันที่ใช้อยู่ไม่มี key 'th' โดยตรง)
            lang='latin',
            use_angle_cls=False,
            use_gpu=False,
            show_log=False,
        )
    return ocr

@app.get("/")
def root():
    return {"service": "Thai OCR Service", "status": "running"}

@app.get("/health")
def health():
    try:
        return {"status": "ok", "ocr_ready": get_ocr() is not None}
    except:
        return {"status": "error"}, 503

@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    try:
        ocr_instance = get_ocr()

        image_bytes = await file.read()

        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        temp_path = "/tmp/ocr_temp.jpg"
        image.save(temp_path, "JPEG")

        result = ocr_instance.ocr(temp_path, cls=False)

        lines = []
        if result and result[0]:
            for line in result[0]:
                text = line[1][0]
                conf = line[1][1]
                if conf > 0.3:
                    lines.append(text)

        full_text = "\n".join(lines)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return {"text": full_text, "lines": len(lines), "characters": len(full_text)}

    except Exception as e:
        logger.error(f"OCR Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT") or 5000)
    uvicorn.run("main:app", host="0.0.0.0", port=port)
