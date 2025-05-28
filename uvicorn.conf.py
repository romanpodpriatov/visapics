# Uvicorn configuration for production deployment
import os

# Server configuration
host = "0.0.0.0"
port = 8000
backlog = 2048

# Worker configuration optimized for dedicated server: 32GB RAM, 8 cores
workers = 1  # Keep single worker for SocketIO compatibility
worker_class = "uvicorn.workers.UvicornWorker"

# Timeout configuration - crucial for fixing WebSocket timeout issues
timeout_keep_alive = 600  # 10 minutes for heavy AI processing
timeout_graceful_shutdown = 30

# SSL configuration (handled by nginx)
ssl_keyfile = None
ssl_certfile = None

# Application configuration
app_module = "main:app"

# Logging configuration
log_level = "info"
access_log = True
use_colors = False

# Performance optimizations
loop = "uvloop"  # Use uvloop for better performance
http = "httptools"  # Use httptools for better HTTP parsing

# Limit configuration
limit_concurrency = 2000
limit_max_requests = 500

# Development vs Production
reload = False
debug = False

# WebSocket configuration - synchronized ping/timeout settings
ws_ping_interval = 25  # Send ping every 25 seconds - matches socketio
ws_ping_timeout = 65   # Wait up to 65 seconds for pong response - slightly higher than socketio
ws_max_size = 16777216  # 16MB max message size

def get_config():
    """Return uvicorn configuration dictionary"""
    return {
        "host": host,
        "port": port,
        "workers": workers,
        "app": app_module,
        "log_level": log_level,
        "access_log": access_log,
        "use_colors": use_colors,
        "loop": loop,
        "http": http,
        "ws_ping_interval": ws_ping_interval,
        "ws_ping_timeout": ws_ping_timeout,
        "ws_max_size": ws_max_size,
        "timeout_keep_alive": timeout_keep_alive,
        "limit_concurrency": limit_concurrency,
        "limit_max_requests": limit_max_requests,
        "reload": reload,
        "ssl_keyfile": ssl_keyfile,
        "ssl_certfile": ssl_certfile,
    }