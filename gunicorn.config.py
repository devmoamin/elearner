import multiprocessing

wsgi_app = "elearner.wsgi:application"
bind = "0.0.0.0:8001"  # Bind to localhost port 8001
workers = multiprocessing.cpu_count() * 2 + 1  # Recommended formula for workers
worker_class = "sync"  # Default worker class
threads = 2  # Number of threads per worker
timeout = 30  # Time in seconds for a request to complete
accesslog = "/var/log/elearner/gunicorn/access.log"  # Log file for access logs
errorlog = "/var/log/elearner/gunicorn/error.log"  # Log file for error logs
loglevel = "info"  # Logging level: debug, info, warning, error, critical
# Redirect stdout/stderr to log file
capture_output = True
# Daemonize the Gunicorn process (detach & enter background)
daemon = True
