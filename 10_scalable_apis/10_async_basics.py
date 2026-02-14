"""
10. Scalable APIs - Async Basics
================================

This module demonstrates the differences between async def and def,
and shows how to use them effectively in FastAPI.

Topics covered:
- Synchronous vs Asynchronous endpoints
- Event loop basics
- Performance comparison
- When to use each approach
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
import time
import asyncio
from datetime import datetime
from typing import List
import httpx

app = FastAPI(title="Async Basics API", version="1.0.0")


# ============================================================================
# SECTION 1: Synchronous vs Asynchronous Endpoints
# ============================================================================

@app.get("/sync/sleep")
def sync_sleep_endpoint(seconds: int = 1):
    """
    Synchronous endpoint that blocks the thread.
    
    FastAPI runs this in a thread pool executor.
    Each request consumes a thread from the pool.
    """
    start = time.time()
    time.sleep(seconds)  # Blocks the thread
    duration = time.time() - start
    
    return {
        "message": "Sync sleep completed",
        "requested_seconds": seconds,
        "actual_duration": round(duration, 2),
        "endpoint_type": "synchronous",
        "note": "This blocks a thread from the thread pool"
    }


@app.get("/async/sleep")
async def async_sleep_endpoint(seconds: int = 1):
    """
    Asynchronous endpoint that doesn't block the event loop.
    
    During await, the event loop can handle other requests.
    Thousands of these can run concurrently.
    """
    start = time.time()
    await asyncio.sleep(seconds)  # Yields control to event loop
    duration = time.time() - start
    
    return {
        "message": "Async sleep completed",
        "requested_seconds": seconds,
        "actual_duration": round(duration, 2),
        "endpoint_type": "asynchronous",
        "note": "This yields control to the event loop"
    }


# ============================================================================
# SECTION 2: CPU-Bound Operations
# ============================================================================

def calculate_fibonacci(n: int) -> int:
    """Calculate fibonacci number (CPU-intensive)"""
    if n <= 1:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)


@app.get("/sync/fibonacci/{n}")
def sync_fibonacci(n: int):
    """
    Synchronous CPU-bound operation.
    
    This is the CORRECT approach for CPU-intensive tasks.
    FastAPI automatically runs this in a thread pool.
    """
    if n > 35:
        return {"error": "n too large (max 35 to prevent timeout)"}
    
    start = time.time()
    result = calculate_fibonacci(n)
    duration = time.time() - start
    
    return {
        "n": n,
        "fibonacci": result,
        "calculation_time": round(duration, 4),
        "note": "CPU-bound operations should use 'def', not 'async def'"
    }


@app.get("/async/fibonacci/{n}")
async def async_fibonacci_wrong(n: int):
    """
    ❌ WRONG: Async CPU-bound operation.
    
    This is an ANTI-PATTERN!
    CPU-intensive work in async functions blocks the event loop.
    """
    if n > 35:
        return {"error": "n too large (max 35 to prevent timeout)"}
    
    start = time.time()
    result = calculate_fibonacci(n)  # Blocks event loop!
    duration = time.time() - start
    
    return {
        "n": n,
        "fibonacci": result,
        "calculation_time": round(duration, 4),
        "WARNING": "This blocks the event loop - BAD PRACTICE!",
        "note": "CPU-bound work should use 'def', not 'async def'"
    }


# ============================================================================
# SECTION 3: I/O-Bound Operations
# ============================================================================

@app.get("/sync/http-request")
def sync_http_request():
    """
    Synchronous HTTP request using requests library.
    
    Blocks the thread while waiting for response.
    Thread is idle but still consuming resources.
    """
    import requests
    
    start = time.time()
    try:
        response = requests.get("https://httpbin.org/delay/1", timeout=5)
        duration = time.time() - start
        
        return {
            "status_code": response.status_code,
            "duration": round(duration, 2),
            "endpoint_type": "synchronous",
            "note": "Thread was blocked waiting for HTTP response"
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/async/http-request")
async def async_http_request():
    """
    Asynchronous HTTP request using httpx.
    
    During the HTTP request, event loop can handle other requests.
    Much more efficient for I/O-bound operations.
    """
    start = time.time()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://httpbin.org/delay/1", timeout=5)
            duration = time.time() - start
            
            return {
                "status_code": response.status_code,
                "duration": round(duration, 2),
                "endpoint_type": "asynchronous",
                "note": "Event loop handled other requests during HTTP wait"
            }
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# SECTION 4: Multiple Concurrent Operations
# ============================================================================

async def fetch_user_data(user_id: int) -> dict:
    """Simulate fetching user data from database"""
    await asyncio.sleep(0.1)  # Simulate DB query delay
    return {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com"
    }


async def fetch_user_orders(user_id: int) -> List[dict]:
    """Simulate fetching user orders from database"""
    await asyncio.sleep(0.15)  # Simulate DB query delay
    return [
        {"id": 1, "total": 99.99, "status": "completed"},
        {"id": 2, "total": 149.99, "status": "pending"}
    ]


async def fetch_user_reviews(user_id: int) -> List[dict]:
    """Simulate fetching user reviews from database"""
    await asyncio.sleep(0.12)  # Simulate DB query delay
    return [
        {"product_id": 101, "rating": 5, "comment": "Great!"},
        {"product_id": 102, "rating": 4, "comment": "Good"}
    ]


@app.get("/sync/user-dashboard/{user_id}")
def sync_user_dashboard(user_id: int):
    """
    Synchronous approach - operations run sequentially.
    
    Total time = sum of all operations (0.1 + 0.15 + 0.12 = 0.37s)
    """
    import asyncio
    
    start = time.time()
    
    # These run ONE AFTER ANOTHER
    user = asyncio.run(fetch_user_data(user_id))
    orders = asyncio.run(fetch_user_orders(user_id))
    reviews = asyncio.run(fetch_user_reviews(user_id))
    
    duration = time.time() - start
    
    return {
        "user": user,
        "orders": orders,
        "reviews": reviews,
        "fetch_time": round(duration, 2),
        "note": "Sequential execution - slow!"
    }


@app.get("/async/user-dashboard/{user_id}")
async def async_user_dashboard(user_id: int):
    """
    Asynchronous approach - operations run concurrently.
    
    Total time = max of all operations (0.15s, not 0.37s)
    This is 2.5x faster!
    """
    start = time.time()
    
    # These run CONCURRENTLY
    user, orders, reviews = await asyncio.gather(
        fetch_user_data(user_id),
        fetch_user_orders(user_id),
        fetch_user_reviews(user_id)
    )
    
    duration = time.time() - start
    
    return {
        "user": user,
        "orders": orders,
        "reviews": reviews,
        "fetch_time": round(duration, 2),
        "note": "Concurrent execution - fast!"
    }


# ============================================================================
# SECTION 5: Event Loop Demonstration
# ============================================================================

@app.get("/event-loop/demo")
async def event_loop_demo():
    """
    Demonstrates how the event loop handles multiple tasks.
    """
    tasks_log = []
    
    async def task(name: str, delay: float):
        tasks_log.append(f"{name} started at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        await asyncio.sleep(delay)
        tasks_log.append(f"{name} finished at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        return f"{name} result"
    
    start = time.time()
    
    # Run three tasks concurrently
    results = await asyncio.gather(
        task("Task-A", 0.3),
        task("Task-B", 0.2),
        task("Task-C", 0.1)
    )
    
    duration = time.time() - start
    
    return {
        "results": results,
        "total_time": round(duration, 2),
        "execution_log": tasks_log,
        "explanation": "All tasks started immediately, finished based on their delay"
    }


# ============================================================================
# SECTION 6: Mixing Sync and Async
# ============================================================================

def blocking_operation():
    """A blocking operation that should not be in async context"""
    time.sleep(1)
    return "Blocking operation completed"


@app.get("/mixed/wrong")
async def mixed_wrong():
    """
    ❌ WRONG: Calling blocking function in async endpoint
    
    This blocks the event loop!
    """
    start = time.time()
    result = blocking_operation()  # This blocks!
    duration = time.time() - start
    
    return {
        "result": result,
        "duration": round(duration, 2),
        "WARNING": "This blocked the event loop - BAD PRACTICE!"
    }


@app.get("/mixed/correct")
async def mixed_correct():
    """
    ✅ CORRECT: Running blocking function in thread pool
    
    This doesn't block the event loop.
    """
    start = time.time()
    
    # Run blocking operation in a thread pool
    result = await asyncio.to_thread(blocking_operation)
    
    duration = time.time() - start
    
    return {
        "result": result,
        "duration": round(duration, 2),
        "note": "Blocking operation ran in thread pool - event loop not blocked"
    }


# ============================================================================
# SECTION 7: Performance Comparison Endpoint
# ============================================================================

@app.get("/compare/sync-vs-async")
async def compare_sync_vs_async(requests: int = 5):
    """
    Compare synchronous vs asynchronous execution for multiple requests.
    
    This demonstrates the power of async for concurrent I/O operations.
    """
    if requests > 20:
        return {"error": "Maximum 20 requests allowed for this demo"}
    
    async def async_operation():
        await asyncio.sleep(0.1)
        return "done"
    
    def sync_operation():
        time.sleep(0.1)
        return "done"
    
    # Test async (concurrent)
    start_async = time.time()
    await asyncio.gather(*[async_operation() for _ in range(requests)])
    async_duration = time.time() - start_async
    
    # Test sync (sequential)
    start_sync = time.time()
    for _ in range(requests):
        sync_operation()
    sync_duration = time.time() - start_sync
    
    improvement = ((sync_duration - async_duration) / sync_duration) * 100
    
    return {
        "requests_count": requests,
        "async_time": round(async_duration, 2),
        "sync_time": round(sync_duration, 2),
        "speedup": f"{round(sync_duration / async_duration, 1)}x faster",
        "improvement": f"{round(improvement, 1)}% faster",
        "explanation": f"Async handled {requests} operations concurrently while sync did them one by one"
    }


# ============================================================================
# SECTION 8: Best Practices
# ============================================================================

@app.get("/best-practices")
async def best_practices():
    """
    Returns best practices for choosing between sync and async.
    """
    return {
        "use_async_def_when": [
            "Making database queries (with async drivers)",
            "Calling external APIs",
            "Reading/writing files (with aiofiles)",
            "WebSocket connections",
            "High concurrency requirements",
            "I/O-bound operations"
        ],
        "use_def_when": [
            "CPU-intensive calculations",
            "Using synchronous libraries (requests, sqlite3, etc.)",
            "Simple operations with no I/O",
            "Data processing and transformations"
        ],
        "anti_patterns": [
            "❌ Using time.sleep() in async def",
            "❌ Using synchronous libraries (requests) in async def",
            "❌ Using async def for CPU-bound operations",
            "❌ Not using await with async operations",
            "❌ Blocking the event loop with long-running sync operations"
        ],
        "performance_tips": [
            "✅ Use asyncio.gather() for concurrent operations",
            "✅ Use connection pooling for databases",
            "✅ Set timeouts on external requests",
            "✅ Use async libraries (httpx, asyncpg, aiofiles)",
            "✅ Run CPU-bound work in thread pool with asyncio.to_thread()"
        ]
    }


# ============================================================================
# Health Check
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "title": "Async Basics API",
        "description": "Learn the differences between sync and async in FastAPI",
        "endpoints": {
            "sync_sleep": "/sync/sleep?seconds=1",
            "async_sleep": "/async/sleep?seconds=1",
            "sync_fibonacci": "/sync/fibonacci/30",
            "async_fibonacci": "/async/fibonacci/30",
            "sync_http": "/sync/http-request",
            "async_http": "/async/http-request",
            "sync_dashboard": "/sync/user-dashboard/1",
            "async_dashboard": "/async/user-dashboard/1",
            "event_loop_demo": "/event-loop/demo",
            "comparison": "/compare/sync-vs-async?requests=5",
            "best_practices": "/best-practices"
        },
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("🚀 Starting Async Basics API")
    print("="*70)
    print("\nTry these endpoints to see the difference:")
    print("  • http://localhost:8000/docs - Interactive API documentation")
    print("  • http://localhost:8000/compare/sync-vs-async?requests=5")
    print("  • http://localhost:8000/async/user-dashboard/1")
    print("  • http://localhost:8000/event-loop/demo")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
