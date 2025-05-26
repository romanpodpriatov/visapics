# Multi-stage build for production deployment
FROM python:3.9-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p uploads processed previews gfpgan/weights models fonts

# Copy application code
COPY . .

# Download models if they don't exist (for fresh deployments)
RUN python -c "
import os
import urllib.request

# Create model directories
os.makedirs('gfpgan/weights', exist_ok=True)
os.makedirs('models', exist_ok=True)

# Download GFPGAN model if not present
gfpgan_path = 'gfpgan/weights/GFPGANv1.4.pth'
if not os.path.exists(gfpgan_path):
    print('Downloading GFPGAN model...')
    urllib.request.urlretrieve(
        'https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth',
        gfpgan_path
    )

# Note: BiRefNet model needs to be manually added or downloaded from your source
print('Model setup complete. BiRefNet model should be manually added to models/ directory.')
"

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "main.py"]