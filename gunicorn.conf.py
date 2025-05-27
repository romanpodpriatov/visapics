# Gunicorn configuration for production deployment
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Optimized for dedicated server: 32GB RAM, 8 cores
workers = 1  # Keep single worker for SocketIO compatibility
worker_class = "eventlet"  # Required for SocketIO support
worker_connections = 2000  # High concurrent connections
timeout = 600  # 10 minutes for heavy AI processing
keepalive = 5

# Memory management for high-performance server
max_requests = 500  # Higher threshold for powerful server
max_requests_jitter = 50
worker_tmp_dir = "/dev/shm"  # Use shared memory for tmp files

# Performance optimizations
preload_app = True  # Preload models once, share across workers
worker_rlimit_nofile = 65535  # High file descriptor limit

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "visapics"

# Server mechanics
preload_app = True
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (handled by nginx)
keyfile = None
certfile = None

# Memory and performance optimizations
worker_tmp_dir = "/dev/shm"
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

# Graceful shutdown
graceful_timeout = 30

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker aborted (pid: %s)", worker.pid)