"""
Request Timing Middleware

This module demonstrates various timing and performance tracking patterns:
- Basic request timing
- Detailed timing with breakdown
- Performance metrics collection
- Timeout enforcement
- Response time statistics
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import time
import asyncio
from typing import Callable, Dict, List
from collections import defaultdict
from datetime import datetime
import statistics

app = FastAPI(
    title="Request Timing Middleware API",
    version="1.0.0",
    description="Demonstrates timing and performance tracking middleware"
)

# Global statistics storage (in production, use Redis or a proper database)
request_stats: Dict[str, List[float]] = defaultdict(list)
total_requests = 0
total_time = 0.0


# ============================================================================
# BASIC TIMING MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def basic_timing(request: Request, call_next: Callable):
    """
    Simple timing middleware that adds X-Process-Time header.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Add timing header
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    
    return response


# ============================================================================
# DETAILED TIMING MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def detailed_timing(request: Request, call_next: Callable):
    """
    Detailed timing middleware that tracks multiple phases.
    """
    timings = {}
    
    # Track middleware start
    request_start = time.time()
    timings['middleware_start'] = request_start
    
    # Store timing info in request state
    request.state.timings = timings
    request.state.request_start = request_start
    
    # Process request
    response = await call_next(request)
    
    # Calculate total time
    request_end = time.time()
    total_time = request_end - request_start
    
    # Add detailed timing headers
    response.headers["X-Total-Time"] = f"{total_time:.4f}"
    response.headers["X-Timestamp"] = datetime.now().isoformat()
    
    return response


# ============================================================================
# STATISTICS COLLECTION MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def collect_statistics(request: Request, call_next: Callable):
    """
    Collects request timing statistics for analysis.
    """
    global total_requests, total_time
    
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate timing
    process_time = time.time() - start_time
    
    # Collect statistics
    endpoint = request.url.path
    request_stats[endpoint].append(process_time)
    total_requests += 1
    total_time += process_time
    
    # Add statistics headers
    endpoint_stats = request_stats[endpoint]
    if len(endpoint_stats) > 0:
        avg_time = statistics.mean(endpoint_stats)
        response.headers["X-Endpoint-Avg-Time"] = f"{avg_time:.4f}"
        response.headers["X-Endpoint-Request-Count"] = str(len(endpoint_stats))
    
    return response


# ============================================================================
# TIMEOUT ENFORCEMENT MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def enforce_timeout(request: Request, call_next: Callable):
    """
    Enforces a maximum request timeout.
    
    If a request takes longer than the timeout, it's cancelled
    and a 504 Gateway Timeout is returned.
    """
    # Set timeout (in seconds)
    timeout = 10.0
    
    try:
        # Use asyncio.wait_for to enforce timeout
        response = await asyncio.wait_for(
            call_next(request),
            timeout=timeout
        )
        return response
        
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=504,
            content={
                "error": "Request timeout",
                "message": f"Request exceeded {timeout} seconds timeout",
                "endpoint": request.url.path
            }
        )


# ============================================================================
# PERFORMANCE TRACKING MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def performance_tracking(request: Request, call_next: Callable):
    """
    Tracks performance and adds warnings for slow requests.
    """
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate timing
    process_time = time.time() - start_time
    
    # Categorize performance
    if process_time < 0.1:
        performance = "excellent"
    elif process_time < 0.5:
        performance = "good"
    elif process_time < 1.0:
        performance = "acceptable"
    elif process_time < 3.0:
        performance = "slow"
    else:
        performance = "very-slow"
    
    # Add performance headers
    response.headers["X-Performance"] = performance
    response.headers["X-Process-Time-Ms"] = f"{process_time * 1000:.2f}"
    
    # Add warning header for slow requests
    if performance in ["slow", "very-slow"]:
        response.headers["X-Performance-Warning"] = (
            f"Request took {process_time:.2f}s - Consider optimization"
        )
    
    return response


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint for basic testing."""
    return {
        "message": "Request Timing Middleware API",
        "tip": "Check response headers for timing information"
    }


@app.get("/fast")
async def fast_endpoint():
    """Very fast endpoint (< 0.1s)."""
    return {
        "message": "Fast response",
        "expected_performance": "excellent"
    }


@app.get("/medium")
async def medium_endpoint():
    """Medium speed endpoint (~0.5s)."""
    await asyncio.sleep(0.5)
    return {
        "message": "Medium speed response",
        "expected_performance": "good to acceptable"
    }


@app.get("/slow")
async def slow_endpoint():
    """Slow endpoint (~2s)."""
    await asyncio.sleep(2)
    return {
        "message": "Slow response",
        "expected_performance": "slow",
        "delay": "2 seconds"
    }


@app.get("/very-slow")
async def very_slow_endpoint():
    """Very slow endpoint (~5s)."""
    await asyncio.sleep(5)
    return {
        "message": "Very slow response",
        "expected_performance": "very-slow",
        "delay": "5 seconds"
    }


@app.get("/timeout-test")
async def timeout_test():
    """
    Endpoint that exceeds timeout (will fail).
    Default timeout is 10 seconds, this sleeps for 15.
    """
    await asyncio.sleep(15)
    return {"message": "This should timeout"}


@app.get("/cpu-intensive")
async def cpu_intensive():
    """
    Simulates CPU-intensive operation.
    """
    start = time.time()
    
    # Simulate CPU work
    total = 0
    for i in range(10000000):
        total += i
    
    elapsed = time.time() - start
    
    return {
        "message": "CPU-intensive operation completed",
        "computation_time": f"{elapsed:.4f}s",
        "result": total
    }


@app.get("/database-simulation")
async def database_simulation():
    """
    Simulates database query with varying response times.
    """
    import random
    
    # Simulate variable database response time (0.1 to 1.0 seconds)
    query_time = random.uniform(0.1, 1.0)
    await asyncio.sleep(query_time)
    
    return {
        "message": "Database query completed",
        "query_time": f"{query_time:.4f}s",
        "records": 42
    }


@app.get("/statistics")
async def get_statistics():
    """
    Returns timing statistics for all endpoints.
    """
    stats = {}
    
    for endpoint, times in request_stats.items():
        if len(times) > 0:
            stats[endpoint] = {
                "count": len(times),
                "avg_time": f"{statistics.mean(times):.4f}s",
                "min_time": f"{min(times):.4f}s",
                "max_time": f"{max(times):.4f}s",
            }
            
            if len(times) >= 2:
                stats[endpoint]["std_dev"] = f"{statistics.stdev(times):.4f}s"
    
    return {
        "total_requests": total_requests,
        "total_time": f"{total_time:.4f}s",
        "average_time": f"{(total_time / total_requests if total_requests > 0 else 0):.4f}s",
        "endpoints": stats
    }


@app.post("/reset-statistics")
async def reset_statistics():
    """Reset all timing statistics."""
    global total_requests, total_time
    request_stats.clear()
    total_requests = 0
    total_time = 0.0
    
    return {"message": "Statistics reset successfully"}


# ============================================================================
# TIMED OPERATION HELPER
# ============================================================================

class Timer:
    """
    Context manager for timing code blocks.
    Can be used in endpoints to track specific operations.
    """
    def __init__(self, name: str, request: Request = None):
        self.name = name
        self.request = request
        self.start_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        self.elapsed = time.time() - self.start_time
        if self.request and hasattr(self.request.state, 'timings'):
            self.request.state.timings[self.name] = self.elapsed


@app.get("/timed-operations")
async def timed_operations(request: Request):
    """
    Demonstrates timing specific operations within an endpoint.
    """
    results = {}
    
    # Time database operation
    with Timer("database", request) as t:
        await asyncio.sleep(0.3)
        results["database"] = f"{t.elapsed:.4f}s"
    
    # Time external API call
    with Timer("external_api", request) as t:
        await asyncio.sleep(0.2)
        results["external_api"] = f"{t.elapsed:.4f}s"
    
    # Time data processing
    with Timer("processing", request) as t:
        await asyncio.sleep(0.1)
        results["processing"] = f"{t.elapsed:.4f}s"
    
    return {
        "message": "Operations completed",
        "timings": results,
        "tip": "Check X-Total-Time header for overall request time"
    }


# ============================================================================
# STARTUP EVENT
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize timing system."""
    print("🚀 Request Timing Middleware API Started")
    print("⏱️  All requests are being timed")
    print("📊 Statistics are collected per endpoint")
    print("\nPerformance categories:")
    print("  < 0.1s  = excellent")
    print("  < 0.5s  = good")
    print("  < 1.0s  = acceptable")
    print("  < 3.0s  = slow")
    print("  >= 3.0s = very-slow")
    print("\n🔍 Check response headers for:")
    print("  X-Process-Time")
    print("  X-Performance")
    print("  X-Endpoint-Avg-Time")


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\nTest endpoints:")
    print("  GET  /fast               - Fast endpoint (< 0.1s)")
    print("  GET  /medium             - Medium endpoint (~0.5s)")
    print("  GET  /slow               - Slow endpoint (~2s)")
    print("  GET  /very-slow          - Very slow endpoint (~5s)")
    print("  GET  /cpu-intensive      - CPU-intensive operation")
    print("  GET  /database-simulation - Simulated DB query")
    print("  GET  /timed-operations   - Multiple timed operations")
    print("  GET  /statistics         - View timing statistics")
    print("  POST /reset-statistics   - Reset statistics")
    print("  GET  /docs               - API documentation")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
