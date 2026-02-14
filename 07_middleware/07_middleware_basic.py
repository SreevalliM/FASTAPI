"""
FastAPI Middleware Basics

This module demonstrates the fundamentals of middleware in FastAPI:
- Custom logging middleware
- Request timing middleware
- CORS middleware configuration
- Built-in middleware usage
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time
import logging
from typing import Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Middleware Basics API", version="1.0.0")


# ============================================================================
# CUSTOM MIDDLEWARE - Basic Request Logging
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next: Callable):
    """
    Simple logging middleware that logs every request.
    
    Middleware processes requests before they reach the endpoint
    and responses before they're sent to the client.
    """
    # Log incoming request
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    logger.info(f"Client: {request.client.host}")
    
    # Call the next middleware or endpoint
    response = await call_next(request)
    
    # Log outgoing response
    logger.info(f"Response status: {response.status_code}")
    
    return response


# ============================================================================
# CUSTOM MIDDLEWARE - Request Timing
# ============================================================================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable):
    """
    Middleware that measures request processing time.
    
    Adds a custom header 'X-Process-Time' to the response
    indicating how long the request took to process.
    """
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Add custom header
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    
    logger.info(f"Request processed in {process_time:.4f} seconds")
    
    return response


# ============================================================================
# BUILT-IN MIDDLEWARE - CORS Configuration
# ============================================================================

# CORS (Cross-Origin Resource Sharing) middleware
# This should be added AFTER custom middleware definitions
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default
        "http://localhost:8080",  # Vue default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# ============================================================================
# BUILT-IN MIDDLEWARE - GZip Compression
# ============================================================================

# Compress responses larger than 1000 bytes
app.add_middleware(GZipMiddleware, minimum_size=1000)


# ============================================================================
# BUILT-IN MIDDLEWARE - Trusted Host
# ============================================================================

# Protect against Host header attacks
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.example.com"]
)


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Simple root endpoint to test middleware."""
    return {
        "message": "Middleware Basics API",
        "tip": "Check response headers for X-Process-Time"
    }


@app.get("/slow")
async def slow_endpoint():
    """
    Endpoint that simulates slow processing.
    Check the X-Process-Time header to see the delay.
    """
    # Simulate slow processing
    time.sleep(2)
    return {
        "message": "This endpoint took 2 seconds to process",
        "tip": "Check the X-Process-Time header"
    }


@app.get("/fast")
async def fast_endpoint():
    """Fast endpoint for timing comparison."""
    return {
        "message": "This endpoint is fast!",
        "processing": "Almost instant"
    }


@app.post("/data")
async def post_data(data: dict):
    """
    POST endpoint to test CORS.
    Try calling this from a web browser at a different origin.
    """
    logger.info(f"Received data: {data}")
    return {
        "message": "Data received successfully",
        "received": data
    }


@app.get("/large-response")
async def large_response():
    """
    Endpoint that returns a large response.
    GZip middleware will compress this automatically.
    """
    return {
        "message": "Large response to test GZip compression",
        "data": ["item" + str(i) for i in range(1000)],
        "tip": "This response should be compressed by GZip middleware"
    }


# ============================================================================
# STARTUP AND SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Runs when the application starts."""
    logger.info("Application started - Middleware is active")
    logger.info("Available middleware:")
    logger.info("  - Request Logging")
    logger.info("  - Request Timing")
    logger.info("  - CORS")
    logger.info("  - GZip Compression")
    logger.info("  - Trusted Host")


@app.on_event("shutdown")
async def shutdown_event():
    """Runs when the application shuts down."""
    logger.info("Application shutting down")


# ============================================================================
# RUNNING THE APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Middleware Basics API...")
    print("📝 Check the console for middleware logs")
    print("🔍 Check response headers for X-Process-Time")
    print("\nAvailable endpoints:")
    print("  GET  /           - Root endpoint")
    print("  GET  /fast       - Fast endpoint")
    print("  GET  /slow       - Slow endpoint (2s delay)")
    print("  POST /data       - Test CORS")
    print("  GET  /large-response - Test GZip compression")
    print("  GET  /docs       - Interactive API documentation")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
