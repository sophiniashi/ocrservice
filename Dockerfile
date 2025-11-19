FROM python:3.11-slim

# Install system dependencies for PyMuPDF
RUN apt-get update && apt-get install -y \
    swig \
    build-essential \
    pkg-config \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip and install Python packages
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy application code
COPY app.py .

# Expose port
EXPOSE $PORT

# Run gunicorn
CMD gunicorn -w 4 -b 0.0.0.0:$PORT app:app

