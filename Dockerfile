# Multi-stage build to reduce final image size
FROM python:3.10-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    swig \
    build-essential \
    pkg-config \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip and install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel

# Install base packages
RUN pip install --no-cache-dir flask==2.3.3 flask-cors==4.0.0 pillow==10.1.0 requests==2.31.0 gunicorn==21.2.0

# Install PyMuPDF (paddleocr requires PyMuPDF<1.21.0)
# Note: PaddleOCR uses PaddlePaddle (installed automatically), not PyTorch
RUN pip install --no-cache-dir --prefer-binary "PyMuPDF==1.20.2" || \
    (echo "Wheel not available, building from source..." && \
     pip install --no-cache-dir "PyMuPDF==1.20.2")

# Install paddleocr (will use the PyMuPDF we just installed)
# Note: PaddleOCR will download models on first use, but we'll use Lite models
RUN pip install --no-cache-dir paddleocr==2.7.0.3

# Final stage - minimal runtime image
FROM python:3.10-slim

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y \
    libfreetype6 \
    libjpeg62-turbo \
    zlib1g \
    libffi8 \
    libssl3 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY app.py start.sh ./

# Make start script executable
RUN chmod +x start.sh

# Clean up Python cache
RUN find /usr/local/lib/python3.10 -name "*.pyc" -delete \
    && find /usr/local/lib/python3.10 -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Expose port (Railway will set PORT env var at runtime)
# Using default port 5000 for documentation, actual port comes from $PORT env var
EXPOSE 5000

# Run start script which handles PORT variable
CMD ["./start.sh"]

