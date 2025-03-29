bind = '0.0.0.0:5000'  # Bind to 0.0.0.0 on port 8000
workers = 3  # Number of worker processes
threads = 2  # Number of threads per worker
timeout = 30  # Timeout in seconds for each worker
loglevel = 'info'  # Log level (debug, info, warning, error, critical)
accesslog = '-'  # Log access requests to stdout
errorlog = '-'  # Log errors to stderr
