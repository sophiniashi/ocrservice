from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
from PIL import Image
import io
import os
import logging
import re

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


def parse_slip_lines(lines: list[str]) -> dict:
    """
    พยายามดึงข้อมูลสำคัญจากสลิปโอนเงิน
    - amount: จำนวนเงิน
    - from_account / to_account: เลขบัญชี (หรือรูปแบบ xxx-xxx-1234)
    - datetime_line: บรรทัดที่น่าจะเป็นวันที่/เวลา
    - txn_id: รหัสอ้างอิง (ถ้าพอเดาได้)
    """
    amount = None
    amount_line = None

    # หาเลขแบบ 49.00, 1,234.56 ฯลฯ จากล่างขึ้นบน (ส่วนใหญ่จำนวนเงินอยู่ท้าย ๆ)
    money_pattern = re.compile(r"\d{1,3}(?:[\d,]{0,3})[.,]\d{2}")
    for line in reversed(lines):
        m = money_pattern.search(line)
        if m:
            amount_str = m.group(0).replace(",", "")
            try:
                amount = float(amount_str.replace(",", ""))
                amount_line = line
                break
            except ValueError:
                continue

    # หาเลขบัญชีรูปแบบ xxx-xxx-1234 หรือคล้าย ๆ
    account_pattern = re.compile(r"[xX\d]{2,}-[xX\d]{2,}-[xX\d]{2,}")
    accounts = []
    for line in lines:
        for m in account_pattern.findall(line):
            if m not in accounts:
                accounts.append(m)

    from_account = accounts[0] if len(accounts) >= 1 else None
    to_account = accounts[1] if len(accounts) >= 2 else None

    # เดา datetime จากบรรทัดที่มี ':' และตัวเลขเยอะ ๆ
    datetime_line = None
    for line in lines:
        if ":" in line and sum(ch.isdigit() for ch in line) >= 4:
            datetime_line = line
            break

    # เดา transaction id จากบรรทัดที่มีตัวอักษร+เลขยาว ๆ
    txn_id = None
    for line in lines:
        # ความยาวมากหน่อยและมีทั้งตัวอักษรกับตัวเลข
        if len(line) >= 10 and any(c.isalpha() for c in line) and any(
            c.isdigit() for c in line
        ):
            txn_id = line
            break

    return {
        "amount": amount,
        "amount_line": amount_line,
        "from_account": from_account,
        "to_account": to_account,
        "datetime_line": datetime_line,
        "txn_id": txn_id,
    }

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

        lines: list[str] = []
        if result and result[0]:
            for line in result[0]:
                text = line[1][0]
                conf = line[1][1]
                if conf > 0.3:
                    lines.append(text)

        full_text = "\n".join(lines)

        # ดึงข้อมูลเชิงโครงสร้างจากสลิป
        parsed = parse_slip_lines(lines)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return {
            "text": full_text,
            "lines": len(lines),
            "characters": len(full_text),
            "parsed": parsed,
        }

    except Exception as e:
        logger.error(f"OCR Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT") or 5000)
    uvicorn.run("main:app", host="0.0.0.0", port=port)
