#!/bin/bash
# Start script for Railway deployment
# Railway sets PORT environment variable

# Use PORT from environment or default to 5000
PORT=${PORT:-5000}
echo "Starting gunicorn on port $PORT"

# Start gunicorn with PORT from environment
exec gunicorn -w 2 -b "0.0.0.0:$PORT" app:app --timeout 120
