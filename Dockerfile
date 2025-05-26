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
RUN python -c "\
import os; \
import urllib.request; \
os.makedirs('gfpgan/weights', exist_ok=True); \
os.makedirs('models', exist_ok=True); \
gfpgan_path = 'gfpgan/weights/GFPGANv1.4.pth'; \
print('Model setup complete. Models should be downloaded via deployment scripts.'); \
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