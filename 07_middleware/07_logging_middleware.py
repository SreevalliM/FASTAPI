"""
Advanced Logging Middleware

This module demonstrates advanced logging patterns:
- Detailed request/response logging
- Request ID tracking
- User agent and IP logging
- Error logging and tracking
- Structured logging
"""

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import logging
import time
import uuid
from typing import Callable
import json

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api_requests.log')
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Advanced Logging Middleware API",
    version="1.0.0",
    description="Demonstrates advanced middleware logging patterns"
)


# ============================================================================
# REQUEST ID MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def add_request_id(request: Request, call_next: Callable):
    """
    Adds a unique request ID to every request.
    
    This helps track requests through the system and correlate logs.
    The request ID is added to both the request state and response headers.
    """
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    
    # Store in request state for access in endpoints
    request.state.request_id = request_id
    
    # Process request
    response = await call_next(request)
    
    # Add to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response


# ============================================================================
# DETAILED LOGGING MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def detailed_logging(request: Request, call_next: Callable):
    """
    Comprehensive logging middleware that captures:
    - Request details (method, path, query params, headers)
    - Client information (IP, user agent)
    - Response details (status code, processing time)
    - Request/Response body (for debugging)
    """
    # Get request ID (set by previous middleware)
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Capture request details
    request_info = {
        "request_id": request_id,
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "client_ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "content_type": request.headers.get("content-type", "unknown")
    }
    
    # Log incoming request
    logger.info(f"[{request_id}] Incoming request", extra=request_info)
    
    # Start timer
    start_time = time.time()
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log successful response
        logger.info(
            f"[{request_id}] Request completed - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.4f}s"
        )
        
        return response
        
    except Exception as e:
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log error
        logger.error(
            f"[{request_id}] Request failed - "
            f"Error: {str(e)} - "
            f"Type: {type(e).__name__} - "
            f"Time: {process_time:.4f}s",
            exc_info=True
        )
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "request_id": request_id,
                "message": str(e)
            }
        )


# ============================================================================
# SENSITIVE DATA FILTERING MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def filter_sensitive_logs(request: Request, call_next: Callable):
    """
    Middleware that filters sensitive information from logs.
    
    Demonstrates best practices for logging without exposing secrets.
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Get authorization header (safely)
    auth_header = request.headers.get("authorization", None)
    if auth_header:
        # Log that auth is present, but not the actual token
        logger.info(f"[{request_id}] Request includes authentication")
    
    # Process request
    response = await call_next(request)
    
    return response


# ============================================================================
# PERFORMANCE MONITORING MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def performance_monitoring(request: Request, call_next: Callable):
    """
    Tracks performance metrics for monitoring and alerting.
    
    In production, you'd send these metrics to a monitoring system
    like Prometheus, Datadog, or CloudWatch.
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate metrics
    process_time = time.time() - start_time
    
    # Performance thresholds
    if process_time > 5.0:
        logger.warning(
            f"[{request_id}] SLOW REQUEST - "
            f"{request.method} {request.url.path} - "
            f"Time: {process_time:.4f}s"
        )
    elif process_time > 1.0:
        logger.warning(
            f"[{request_id}] MODERATE REQUEST - "
            f"{request.method} {request.url.path} - "
            f"Time: {process_time:.4f}s"
        )
    
    return response


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root(request: Request):
    """Root endpoint with request ID."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    return {
        "message": "Advanced Logging Middleware API",
        "request_id": request_id,
        "tip": "Check server logs and response headers"
    }


@app.get("/test/{item_id}")
async def get_item(item_id: int, request: Request):
    """
    Endpoint to test detailed logging.
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"[{request_id}] Processing item: {item_id}")
    
    return {
        "item_id": item_id,
        "request_id": request_id,
        "status": "success"
    }


@app.post("/login")
async def login(credentials: dict, request: Request):
    """
    Login endpoint to test sensitive data filtering.
    Note: Password is NOT logged.
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # In real app, validate credentials
    username = credentials.get("username")
    
    # Log username but NOT password
    logger.info(f"[{request_id}] Login attempt for user: {username}")
    
    return {
        "message": "Login processed",
        "request_id": request_id,
        "username": username
    }


@app.get("/slow-query")
async def slow_query(request: Request):
    """
    Endpoint that simulates a slow database query.
    Should trigger performance warning.
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"[{request_id}] Starting slow query...")
    
    # Simulate slow query
    time.sleep(2)
    
    return {
        "message": "Query completed",
        "request_id": request_id
    }


@app.get("/error")
async def trigger_error(request: Request):
    """
    Endpoint that deliberately raises an error.
    Test error logging and handling.
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"[{request_id}] About to raise error...")
    
    # Raise an error
    raise ValueError("This is a test error for logging demonstration")


@app.get("/http-error")
async def http_error(request: Request):
    """
    Endpoint that raises an HTTP exception.
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.warning(f"[{request_id}] Raising HTTP 404 error")
    
    raise HTTPException(
        status_code=404,
        detail="This is a test 404 error"
    )


# ============================================================================
# STARTUP EVENT
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info("="*60)
    logger.info("Advanced Logging Middleware API Started")
    logger.info("="*60)
    logger.info("Logging to: api_requests.log")
    logger.info("Active middleware:")
    logger.info("  - Request ID tracking")
    logger.info("  - Detailed request/response logging")
    logger.info("  - Sensitive data filtering")
    logger.info("  - Performance monitoring")
    logger.info("="*60)


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Advanced Logging Middleware API...")
    print("📝 Logs are written to: api_requests.log")
    print("🔍 Each request gets a unique request ID")
    print("\nTest endpoints:")
    print("  GET  /              - Root endpoint")
    print("  GET  /test/{id}     - Test detailed logging")
    print("  POST /login         - Test sensitive data filtering")
    print("  GET  /slow-query    - Test performance monitoring")
    print("  GET  /error         - Test error logging")
    print("  GET  /http-error    - Test HTTP error logging")
    print("  GET  /docs          - API documentation")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
