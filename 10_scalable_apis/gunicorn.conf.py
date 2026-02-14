"""
Gunicorn Configuration File for Production Deployment
====================================================

This configuration file provides production-ready settings
for running FastAPI with Gunicorn + Uvicorn workers.

Usage:
    gunicorn 10_production_deployment:app -c gunicorn.conf.py

Configuration based on:
- https://docs.gunicorn.org/en/stable/settings.html
- FastAPI deployment best practices
"""

import multiprocessing
import os


# ============================================================================
# Server Socket
# ============================================================================

# The socket to bind
bind = "0.0.0.0:8000"

# The maximum number of pending connections
backlog = 2048


# ============================================================================
# Worker Processes
# ============================================================================

# The number of worker processes for handling requests
# Formula: (2 x $num_cores) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# The type of workers to use
# For FastAPI, use Uvicorn workers (ASGI)
worker_class = "uvicorn.workers.UvicornWorker"

# The maximum number of simultaneous clients (per worker)
worker_connections = 1000

# Workers silent for more than this many seconds are killed and restarted
timeout = 30

# Timeout for graceful workers restart
# After receiving a restart signal, workers have this much time to finish
# serving requests
graceful_timeout = 10

# The number of seconds to wait for requests on a Keep-Alive connection
keepalive = 5


# ============================================================================
# Worker Recycling
# ============================================================================

# Restart workers after this many requests
# Helps prevent memory leaks from accumulating
max_requests = 10000

# Randomize the max_requests to prevent all workers from restarting at once
max_requests_jitter = 1000

# Maximum time (in seconds) a worker can live
# 0 means unlimited
max_worker_lifetime = 0


# ============================================================================
# Security
# ============================================================================

# Switch worker processes to run as this user
# Important: Don't run as root in production!
# user = "www-data"  # Uncomment and set appropriate user

# Switch worker processes to run as this group
# group = "www-data"  # Uncomment and set appropriate group

# Limit the allowed size of an HTTP request header field
limit_request_field_size = 8190

# Limit the number of HTTP request header fields
limit_request_fields = 100

# Limit the allowed size of an HTTP request line
limit_request_line = 4094


# ============================================================================
# Logging
# ============================================================================

# The access log file to write to
# "-" means log to stdout
accesslog = "-"

# The error log file to write to
# "-" means log to stderr
errorlog = "-"

# The granularity of Error log outputs
# Valid log levels: debug, info, warning, error, critical
loglevel = "info"

# The Access log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
# %(h) - Remote address
# %(l) - '-'
# %(u) - User name
# %(t) - Date of the request
# %(r) - Status line (e.g. GET / HTTP/1.1)
# %(s) - Status
# %(b) - Response length
# %(f) - Referer
# %(a) - User agent
# %(D) - Time to serve the request in microseconds

# Disable access log for health checks (reduce log noise)
access_log_format_health = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'


# ============================================================================
# Process Naming
# ============================================================================

# A base to use with setproctitle for process naming
proc_name = "fastapi_scalable_api"


# ============================================================================
# Server Mechanics
# ============================================================================

# Daemonize the Gunicorn process
# For production with systemd/supervisor, keep this False
daemon = False

# A filename to use for the PID file
# If set, a file with the process ID is written
pidfile = None

# The path to a directory to use for the unix sockets
# umask = 0

# A directory to use for temporary request data
tmp_upload_dir = None


# ============================================================================
# Server Hooks
# ============================================================================

def on_starting(server):
    """
    Called just before the master process is initialized.
    """
    print("="*70)
    print("🚀 Gunicorn + Uvicorn Starting")
    print("="*70)
    print(f"Workers: {workers}")
    print(f"Bind: {bind}")
    print(f"Worker class: {worker_class}")
    print(f"Timeout: {timeout}s")
    print("="*70)


def on_reload(server):
    """
    Called to recycle workers during a reload via SIGHUP.
    """
    print("🔄 Reloading workers...")


def when_ready(server):
    """
    Called just after the server is started.
    """
    print("✅ Server is ready to handle requests")
    print("="*70)


def pre_fork(server, worker):
    """
    Called just before a worker is forked.
    """
    pass


def post_fork(server, worker):
    """
    Called just after a worker has been forked.
    """
    print(f"👷 Worker {worker.pid} spawned")


def pre_exec(server):
    """
    Called just before a new master process is forked.
    """
    print("🔧 Forking new master process")


def worker_int(worker):
    """
    Called when a worker receives the SIGINT or SIGQUIT signal.
    """
    print(f"⚠️  Worker {worker.pid} received SIGINT/SIGQUIT")


def worker_abort(worker):
    """
    Called when a worker receives the SIGABRT signal.
    """
    print(f"💥 Worker {worker.pid} received SIGABRT")


def pre_request(worker, req):
    """
    Called just before a worker processes the request.
    """
    # Log can be too verbose, uncomment if needed for debugging
    # worker.log.debug(f"{req.method} {req.path}")
    pass


def post_request(worker, req, environ, resp):
    """
    Called after a worker processes the request.
    """
    # Log can be too verbose, uncomment if needed for debugging
    # worker.log.debug(f"{req.method} {req.path} - {resp.status}")
    pass


def worker_exit(server, worker):
    """
    Called just after a worker has been exited.
    """
    print(f"👋 Worker {worker.pid} exited")


def on_exit(server):
    """
    Called just before the master process exits.
    """
    print("="*70)
    print("👋 Gunicorn shutting down")
    print("="*70)


# ============================================================================
# SSL (HTTPS)
# ============================================================================

# SSL certificate file
# keyfile = "/path/to/keyfile.key"

# SSL key file
# certfile = "/path/to/certfile.crt"

# SSL version to use
# ssl_version = ssl.PROTOCOL_TLSv1_2

# SSL certificate authority file
# ca_certs = "/path/to/ca_certs.crt"

# Validate client certificate
# cert_reqs = ssl.CERT_OPTIONAL


# ============================================================================
# Environment-Specific Configuration
# ============================================================================

# You can override settings based on environment
environment = os.getenv("ENVIRONMENT", "production")

if environment == "development":
    # Development settings
    workers = 2
    loglevel = "debug"
    reload = True
    print("⚙️  Running in DEVELOPMENT mode")

elif environment == "staging":
    # Staging settings
    workers = multiprocessing.cpu_count() + 1
    loglevel = "info"
    print("⚙️  Running in STAGING mode")

elif environment == "production":
    # Production settings (already set above)
    print("⚙️  Running in PRODUCTION mode")


# ============================================================================
# Additional Notes
# ============================================================================

"""
Monitoring and Management:

1. Reload workers gracefully:
   kill -HUP <gunicorn_master_pid>

2. Check worker status:
   ps aux | grep gunicorn

3. Stop gracefully:
   kill -TERM <gunicorn_master_pid>

4. Force stop:
   kill -KILL <gunicorn_master_pid>

5. View logs:
   tail -f /var/log/gunicorn/access.log
   tail -f /var/log/gunicorn/error.log

Systemd Service:

Create /etc/systemd/system/fastapi.service:

[Unit]
Description=FastAPI Scalable API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/fastapi
Environment="PATH=/opt/fastapi/venv/bin"
ExecStart=/opt/fastapi/venv/bin/gunicorn 10_production_deployment:app -c gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target

Then:
sudo systemctl daemon-reload
sudo systemctl enable fastapi
sudo systemctl start fastapi
sudo systemctl status fastapi

Performance Tuning:

1. Adjust workers based on workload:
   - I/O-bound: More workers (2 × CPU + 1)
   - CPU-bound: Fewer workers (= CPU count)

2. Monitor memory usage:
   - Each worker consumes ~50-100 MB
   - Set max_requests to prevent memory leaks

3. Use connection pooling:
   - Database connection pools
   - Redis connection pools

4. Enable HTTP/2:
   - Use nginx or similar reverse proxy

5. Use caching:
   - Redis for session data
   - CDN for static assets
"""
