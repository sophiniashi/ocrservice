# Multi-stage build to reduce final image size
FROM python:3.10-slim as builder

# Install build dependencies (will be removed in final stage)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --force-reinstall "numpy<2" "opencv-python-headless<4.9" && \
    rm -rf /root/.cache/pip

# Final stage - minimal runtime image
FROM python:3.10-slim

# Install only runtime dependencies (no build tools)
# Need libGL for OpenCV (cv2) used inside PaddleOCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY main.py .

# Clean up Python cache, temporary files, and documentation
RUN find /usr/local/lib/python3.10 -name "*.pyc" -delete \
    && find /usr/local/lib/python3.10 -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.10 -name "*.pyo" -delete \
    && find /usr/local/lib/python3.10 -type d -name "test" -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.10 -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.10 -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true \
    && rm -rf /root/.cache/pip \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Expose port
EXPOSE 5000

# Start uvicorn with PORT from environment
# Use shell form to ensure PORT variable is expanded
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-5000}"
