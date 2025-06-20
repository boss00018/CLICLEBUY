import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = "circlebuy"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# SSL (uncomment and update for HTTPS)
# keyfile = "path/to/keyfile"
# certfile = "path/to/certfile"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190