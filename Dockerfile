FROM python:3.10-slim

# Install system dependencies for PyMuPDF and other packages
# Install build dependencies, then remove them after building to save space
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

# Verify swig is installed and accessible
RUN which swig && swig -version

WORKDIR /app

# Upgrade pip and install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel

# Install base packages first
# Using newer versions since pip is upgraded and Python 3.10 supports them
RUN pip install --no-cache-dir flask==2.3.3 flask-cors==4.0.0 pillow==10.1.0 requests==2.31.0 gunicorn==21.2.0

# Install torch CPU-only version (much smaller, ~500MB vs ~2GB+)
# Python 3.10 requires torch >= 1.11.0
# Using CPU-only version explicitly to reduce image size significantly
RUN pip install --no-cache-dir torch==2.1.0+cpu --index-url https://download.pytorch.org/whl/cpu || \
    pip install --no-cache-dir torch==2.1.0

# Install PyMuPDF first (paddleocr requires PyMuPDF<1.21.0)
# Try to use pre-built wheels first, fall back to building from source if needed
# Python 3.10 on Linux should have wheels for PyMuPDF 1.20.2
RUN pip install --no-cache-dir --prefer-binary "PyMuPDF==1.20.2" || \
    (echo "Wheel not available, building from source..." && \
     pip install --no-cache-dir "PyMuPDF==1.20.2")

# Install paddleocr (will use the PyMuPDF we just installed)
# PaddleOCR will install transformers if needed, but we can skip it if not required
RUN pip install --no-cache-dir paddleocr==2.7.0.3

# Remove build dependencies and clean up to reduce image size
RUN apt-get purge -y \
    build-essential \
    gcc \
    g++ \
    make \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache/pip \
    && rm -rf /tmp/* \
    && find /usr/local/lib/python3.10 -name "*.pyc" -delete \
    && find /usr/local/lib/python3.10 -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Copy application code
COPY app.py .

# Expose port
EXPOSE $PORT

# Run gunicorn with fewer workers to reduce memory usage
CMD gunicorn -w 2 -b 0.0.0.0:$PORT --timeout 120 app:app

