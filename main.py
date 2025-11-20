"""
Thai OCR Service for Bank Transfer Slips
รองรับการอ่านสลิปโอนเงินภาษาไทย
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from paddleocr import PaddleOCR
from PIL import Image
import io
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Thai OCR Service", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize PaddleOCR with Thai language support (Lite model)
# Lazy loading - initialize on first request
ocr = None

def get_ocr():
    """Get or initialize PaddleOCR instance (lazy loading)"""
    global ocr
    if ocr is None:
        logger.info("Initializing PaddleOCR with Thai language support...")
        try:
            # Use PP-OCR Lite model for smaller size
            ocr = PaddleOCR(
                lang='th',
                use_angle_cls=False,  # Disable angle classifier to reduce size
                use_gpu=False,
                show_log=False
            )
            logger.info("PaddleOCR initialized successfully!")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}", exc_info=True)
            raise
    return ocr

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "Thai OCR Service",
        "status": "running",
        "endpoints": {
            "/health": "Health check",
            "/ocr": "POST - Process OCR from image"
        }
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    try:
        ocr_instance = get_ocr()
        return {
            "status": "ok",
            "service": "Thai OCR Service",
            "ocr_ready": ocr_instance is not None
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }, 503

@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    """
    Process OCR from image
    Accepts: multipart/form-data with 'file' field
    Returns: JSON with 'text' field containing OCR result
    """
    try:
        # Get OCR instance (lazy initialization)
        ocr_instance = get_ocr()
        
        # Read image file
        image_bytes = await file.read()
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Open image with PIL
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save to temporary file for PaddleOCR
        temp_path = '/tmp/ocr_temp.jpg'
        image.save(temp_path, 'JPEG', quality=95)
        
        logger.info(f"Processing OCR for image: {len(image_bytes)} bytes")
        
        # Run OCR
        result = ocr_instance.ocr(temp_path, cls=False)
        
        # Extract text from result
        # PaddleOCR returns: [[[bbox], (text, confidence)], ...]
        text_lines = []
        if result and result[0]:
            for line in result[0]:
                if line and len(line) >= 2:
                    text = line[1][0]  # Extract text
                    confidence = line[1][1]  # Extract confidence
                    if text and confidence > 0.3:  # Filter low confidence
                        text_lines.append(text)
        
        # Combine all lines
        full_text = '\n'.join(text_lines)
        
        logger.info(f"OCR completed. Found {len(text_lines)} lines, {len(full_text)} characters")
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return JSONResponse({
            "text": full_text,
            "lines": len(text_lines),
            "characters": len(full_text),
            "success": True
        })
        
    except Exception as e:
        logger.error(f"OCR Error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "success": False
            }
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
