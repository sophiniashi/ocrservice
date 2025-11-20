from fastapi import FastAPI, UploadFile, File
from paddleocr import PaddleOCR
import os
from fastapi.responses import JSONResponse

# โหลด OCR lite model (ไทย)
ocr = PaddleOCR(
    lang='th',
    use_angle_cls=True,
    rec=True,
    rec_algorithm='CRNN',  # เบา
    det=True,
    use_gpu=False
)

app = FastAPI()

@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    image_bytes = await file.read()
    with open("temp.jpg", "wb") as f:
        f.write(image_bytes)

    result = ocr.ocr("temp.jpg", cls=True)

    text = []
    for line in result:
        for box in line:
            text.append(box[1][0])

    return JSONResponse({"text": "\n".join(text)})
