"""
Thai OCR Service using PaddleOCR
รองรับการอ่านสลิปภาษาไทยด้วยความแม่นยำสูง
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import base64
import logging
import os
from paddleocr import PaddleOCR

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for Flutter app

# Initialize PaddleOCR lazily to reduce memory usage at startup
# use_angle_cls=True helps with rotated text
# lang='th' for Thai language
# Use lazy initialization to prevent crash on startup
ocr = None

def get_ocr():
    """Get or initialize PaddleOCR instance (lazy loading) with PP-OCR Lite"""
    global ocr
    if ocr is None:
        logger.info("Initializing PaddleOCR PP-OCR Lite with Thai language support...")
        try:
            # Use PP-OCR Lite model (much smaller, ~10MB vs ~100MB+)
            # Lite model is optimized for size and speed
            ocr = PaddleOCR(
                use_angle_cls=False,  # Disable angle classifier to reduce model size
                lang='th', 
                use_gpu=False,
                show_log=False,  # Reduce logging overhead
                use_pdserving=False,  # Don't use serving mode
                det_model_dir=None,  # Use default Lite detection model
                rec_model_dir=None,  # Use default Lite recognition model
                cls_model_dir=None   # No angle classifier (saves space)
            )
            logger.info("PaddleOCR PP-OCR Lite initialized successfully!")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {str(e)}", exc_info=True)
            raise
    return ocr

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Check if service is ready (don't initialize PaddleOCR here)
        return jsonify({
            'status': 'ok',
            'service': 'Thai OCR Service',
            'ocr_initialized': ocr is not None
        })
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 503

@app.route('/ocr', methods=['POST'])
def process_ocr():
    """
    Process OCR from image
    Accepts: multipart/form-data with 'image' field, or JSON with 'image_base64'
    Returns: JSON with 'text' field containing OCR result
    """
    try:
        # Check if image is sent as file or base64
        if 'image' in request.files:
            # Image sent as file
            image_file = request.files['image']
            if image_file.filename == '':
                return jsonify({'error': 'No image file provided'}), 400
            
            # Read image
            image_bytes = image_file.read()
            image = Image.open(io.BytesIO(image_bytes))
            
        elif 'image_base64' in request.json:
            # Image sent as base64
            image_base64 = request.json['image_base64']
            # Remove data URL prefix if present
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            image_bytes = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_bytes))
        else:
            return jsonify({'error': 'No image provided. Send as "image" file or "image_base64" in JSON'}), 400
        
        # Convert PIL Image to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save to temporary file for PaddleOCR
        temp_path = '/tmp/ocr_temp.jpg'
        image.save(temp_path, 'JPEG', quality=95)
        
        logger.info(f"Processing OCR for image: {len(image_bytes)} bytes")
        
        # Get OCR instance (lazy initialization)
        ocr_instance = get_ocr()
        
        # Run OCR (cls=False since we disabled angle classifier)
        result = ocr_instance.ocr(temp_path, cls=False)
        
        # Extract text from result
        # PaddleOCR returns: [[[bbox], (text, confidence)], ...]
        text_lines = []
        if result and result[0]:
            for line in result[0]:
                if line and len(line) >= 2:
                    text = line[1][0]  # Extract text
                    confidence = line[1][1]  # Extract confidence
                    if text and confidence > 0.5:  # Filter low confidence
                        text_lines.append(text)
        
        # Combine all lines
        full_text = '\n'.join(text_lines)
        
        logger.info(f"OCR completed. Found {len(text_lines)} lines, {len(full_text)} characters")
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify({
            'text': full_text,
            'lines': len(text_lines),
            'characters': len(full_text),
            'success': True
        })
        
    except Exception as e:
        logger.error(f"OCR Error: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

if __name__ == '__main__':
    # Run on all interfaces
    # For production, use a proper WSGI server like gunicorn
    # Railway/Render will use PORT environment variable
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

