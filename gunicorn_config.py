# Gunicorn configuration file
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes
workers = 1  # Use only 1 worker on free tier to save memory
worker_class = 'sync'
worker_connections = 1000
timeout = 120  # Increased timeout for model loading
keepalive = 5

# Restart workers after this many requests to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'healthoracle'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Preload app to save memory (but may cause issues with lazy loading)
preload_app = False  # Set to False to allow lazy loading

# SSL (if needed)
keyfile = None
certfile = None
