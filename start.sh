#!/bin/bash
# Start script for Railway deployment
# Railway sets PORT environment variable

PORT=${PORT:-5000}
echo "Starting gunicorn on port $PORT"
exec gunicorn -w 2 -b 0.0.0.0:$PORT app:app --timeout 120
