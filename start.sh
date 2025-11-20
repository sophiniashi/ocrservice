#!/bin/bash
# Start script for Railway deployment
# Railway sets PORT environment variable

# Use PORT from environment or default to 5000
PORT=${PORT:-5000}
echo "Starting gunicorn on port $PORT"

# Start gunicorn with single worker to reduce memory usage
# PaddleOCR uses a lot of memory, so we use only 1 worker
# Increase timeout for PaddleOCR initialization and processing
exec gunicorn -w 1 -b "0.0.0.0:$PORT" app:app --timeout 300 --graceful-timeout 120 --keep-alive 5
