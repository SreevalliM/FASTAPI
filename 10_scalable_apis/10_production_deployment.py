"""
10. Scalable APIs - Production Deployment Configuration
=======================================================

This module provides production-ready configuration examples.

Covered:
- Gunicorn + Uvicorn workers
- Configuration for production
- Health checks and monitoring
- Graceful shutdown
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging
import time
import psutil
import os
from datetime import datetime
from contextlib import asynccontextmanager

# ============================================================================
# Logging Configuration
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        # In production, also log to file
        # logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)


# ============================================================================
# Application Lifespan
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan (startup/shutdown).
    
    This is the modern way to handle startup/shutdown events.
    """
    # Startup
    logger.info("="*70)
    logger.info("🚀 Application Starting")
    logger.info("="*70)
    logger.info(f"Python PID: {os.getpid()}")
    logger.info(f"Worker class: Uvicorn (ASGI)")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")
    
    # Initialize resources
    # - Database connection pools
    # - Redis connections
    # - ML model loading
    # - Cache warming
    
    logger.info("✅ Application started successfully")
    logger.info("="*70)
    
    yield
    
    # Shutdown
    logger.info("="*70)
    logger.info("👋 Application Shutting Down")
    logger.info("="*70)
    
    # Cleanup resources
    # - Close database connections
    # - Close Redis connections
    # - Save state if needed
    
    logger.info("✅ Graceful shutdown complete")
    logger.info("="*70)


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Production-Ready Scalable API",
    description="Example of production deployment configuration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ============================================================================
# Middleware Configuration
# ============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourapp.com",
        "https://www.yourapp.com",
        # In development, you might allow localhost
        # "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-Request-ID"]
)

# Gzip Compression
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000  # Only compress responses > 1KB
)


# Request ID Middleware (for tracking)
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID for tracking"""
    import uuid
    request_id = str(uuid.uuid4())
    
    # Store in request state
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response


# Process Time Middleware (for monitoring)
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    
    # Log slow requests
    if process_time > 1.0:
        logger.warning(
            f"Slow request: {request.method} {request.url.path} "
            f"took {round(process_time, 2)}s"
        )
    
    return response


# Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(
        f"Request started: {request.method} {request.url.path} "
        f"[{request_id}] from {request.client.host}"
    )
    
    response = await call_next(request)
    
    logger.info(
        f"Request completed: {request.method} {request.url.path} "
        f"[{request_id}] status={response.status_code}"
    )
    
    return response


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Basic health check endpoint.
    
    Used by:
    - Load balancers
    - Kubernetes liveness probes
    - Monitoring systems
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with system metrics.
    
    Used by:
    - Kubernetes readiness probes
    - Monitoring dashboards
    """
    # Get system metrics
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Check database connection (example)
    # database_healthy = await check_database_connection()
    database_healthy = True  # Placeholder
    
    health_status = {
        "status": "healthy" if database_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime_seconds": time.time() - psutil.Process(os.getpid()).create_time(),
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / (1024 * 1024),
            "disk_percent": disk.percent,
            "disk_free_gb": disk.free / (1024 * 1024 * 1024)
        },
        "services": {
            "database": "healthy" if database_healthy else "unhealthy",
            "cache": "healthy",  # Placeholder
            "external_api": "healthy"  # Placeholder
        }
    }
    
    status_code = 200 if database_healthy else 503
    return JSONResponse(content=health_status, status_code=status_code)


@app.get("/health/ready")
async def readiness_check():
    """
    Readiness check - is the app ready to receive traffic?
    
    Used by Kubernetes to determine if pod should receive traffic.
    """
    # Check critical dependencies
    # database_ready = await check_database_ready()
    # cache_ready = await check_cache_ready()
    
    database_ready = True  # Placeholder
    cache_ready = True
    
    is_ready = database_ready and cache_ready
    
    return JSONResponse(
        content={
            "ready": is_ready,
            "database": database_ready,
            "cache": cache_ready
        },
        status_code=200 if is_ready else 503
    )


@app.get("/health/live")
async def liveness_check():
    """
    Liveness check - is the app alive?
    
    Used by Kubernetes to determine if pod should be restarted.
    Simpler than readiness - just checks if process is running.
    """
    return {"alive": True}


# ============================================================================
# Metrics Endpoint
# ============================================================================

@app.get("/metrics")
async def metrics():
    """
    Expose metrics for monitoring systems (Prometheus, Datadog, etc.)
    
    In production, use proper metrics libraries:
    - prometheus_client
    - statsd
    - datadog
    """
    process = psutil.Process(os.getpid())
    
    memory_info = process.memory_info()
    
    return {
        "process": {
            "pid": os.getpid(),
            "cpu_percent": process.cpu_percent(),
            "memory_mb": memory_info.rss / (1024 * 1024),
            "threads": process.num_threads(),
            "open_files": len(process.open_files())
        },
        "system": {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_mb": psutil.virtual_memory().available / (1024 * 1024)
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Example Business Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Production-Ready Scalable API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "documentation": "/docs",
        "health_check": "/health"
    }


@app.get("/api/data")
async def get_data():
    """Example data endpoint"""
    return {
        "data": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"}
        ],
        "count": 3
    }


# ============================================================================
# Production Configuration Tips
# ============================================================================

@app.get("/production-config")
async def production_config():
    """Production configuration best practices"""
    return {
        "gunicorn_uvicorn": {
            "command": "gunicorn 10_production_deployment:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000",
            "workers": "(2 * CPU_cores) + 1",
            "worker_class": "uvicorn.workers.UvicornWorker",
            "timeout": 30,
            "graceful_timeout": 10,
            "keep_alive": 5
        },
        "environment_variables": {
            "DATABASE_URL": "postgresql://...",
            "REDIS_URL": "redis://...",
            "SECRET_KEY": "Use secrets management (AWS Secrets Manager, etc.)",
            "ENVIRONMENT": "production",
            "LOG_LEVEL": "INFO"
        },
        "docker": {
            "base_image": "python:3.12-slim",
            "expose_port": 8000,
            "health_check": "curl -f http://localhost:8000/health || exit 1",
            "user": "Run as non-root user"
        },
        "kubernetes": {
            "replicas": 3,
            "resources": {
                "requests": {"cpu": "250m", "memory": "256Mi"},
                "limits": {"cpu": "500m", "memory": "512Mi"}
            },
            "probes": {
                "liveness": "/health/live",
                "readiness": "/health/ready"
            }
        },
        "monitoring": {
            "health_checks": "/health, /health/detailed",
            "metrics": "/metrics",
            "logging": "Structured JSON logging",
            "tracing": "OpenTelemetry or similar",
            "alerts": "Error rate, latency, resource usage"
        },
        "security": {
            "https": "Always use HTTPS in production",
            "cors": "Configure allowed origins",
            "rate_limiting": "Implement rate limiting",
            "authentication": "Use OAuth2, JWT, or API keys",
            "secrets": "Never hardcode secrets"
        },
        "performance": {
            "connection_pooling": "For databases and caches",
            "caching": "Redis, Memcached",
            "compression": "GZip middleware",
            "cdn": "For static assets",
            "database_indexes": "On frequently queried columns"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Development server
    print("\n" + "="*70)
    print("🚀 Starting Development Server")
    print("="*70)
    print("\nFor production, use:")
    print("  gunicorn 10_production_deployment:app \\")
    print("    --workers 4 \\")
    print("    --worker-class uvicorn.workers.UvicornWorker \\")
    print("    --bind 0.0.0.0:8000 \\")
    print("    --timeout 30")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(
        "10_production_deployment:app",
        host="0.0.0.0",
        port=8003,
        reload=True,  # Only for development!
        log_level="info"
    )
