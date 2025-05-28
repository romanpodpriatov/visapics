# Multi-stage build for production deployment
FROM python:3.9-slim as base

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-dev \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with uv (much faster than pip)
RUN uv pip install --system --no-cache -r requirements.txt

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
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application with uvicorn - synchronized timeouts
CMD ["uvicorn", "main:asgi_app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--loop", "uvloop", "--http", "httptools", "--ws-ping-interval", "25", "--ws-ping-timeout", "65", "--timeout-keep-alive", "600", "--access-log"]