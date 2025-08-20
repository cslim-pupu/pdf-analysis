# Gunicorn configuration file

# Server socket
bind = "0.0.0.0:5000"

# Worker processes
workers = 1
worker_class = "sync"

# Timeout settings
timeout = 120  # 增加到120秒以处理大文件和多个二维码
keepalive = 2

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "pdf-analysis"

# Worker connections
worker_connections = 1000

# Max requests per worker
max_requests = 1000
max_requests_jitter = 50

# Preload app
preload_app = True