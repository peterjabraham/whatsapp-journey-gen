# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "0.0.0.0:8080"
backlog = 2048

# Worker processes
workers = 2
worker_class = "gevent"  # Use async workers for long-running requests
worker_connections = 1000
timeout = 900  # 15 minutes
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "whatsapp-journey-gen"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

