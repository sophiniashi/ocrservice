FROM python:3.10-slim

# Install system dependencies for PyMuPDF and other packages
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
RUN pip install --no-cache-dir flask==2.0.3 flask-cors==4.0.0 pillow==8.4.0 requests==2.31.0 gunicorn==21.2.0

# Install torch (large package, may take time)
RUN pip install --no-cache-dir torch==2.1.0

# Install transformers
RUN pip install --no-cache-dir transformers==4.35.0

# Install PyMuPDF first (paddleocr requires PyMuPDF<1.21.0)
# Try to use pre-built wheels first, fall back to building from source if needed
# Python 3.10 on Linux should have wheels for PyMuPDF 1.20.2
RUN pip install --no-cache-dir --prefer-binary "PyMuPDF==1.20.2" || \
    (echo "Wheel not available, building from source..." && \
     pip install --no-cache-dir "PyMuPDF==1.20.2")

# Install paddleocr (will use the PyMuPDF we just installed)
RUN pip install --no-cache-dir paddleocr==2.7.0.3

# Copy application code
COPY app.py .

# Expose port
EXPOSE $PORT

# Run gunicorn with fewer workers to reduce memory usage
CMD gunicorn -w 2 -b 0.0.0.0:$PORT --timeout 120 app:app

