"""
10. Scalable APIs - Concurrency Patterns
========================================

This module demonstrates advanced concurrency patterns in FastAPI.

Topics covered:
- asyncio.gather() for parallel execution
- asyncio.wait_for() with timeouts
- Semaphores for rate limiting
- Task management
- Error handling in concurrent operations

Installation:
    pip install httpx aiofiles
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import httpx
import time
from datetime import datetime

app = FastAPI(title="Concurrency Patterns API", version="1.0.0")


# ============================================================================
# SECTION 1: Parallel Execution with asyncio.gather()
# ============================================================================

async def fetch_api_1():
    """Simulates fetching data from API 1"""
    await asyncio.sleep(1)
    return {"source": "API 1", "data": "User profile data"}


async def fetch_api_2():
    """Simulates fetching data from API 2"""
    await asyncio.sleep(1.5)
    return {"source": "API 2", "data": "Order history"}


async def fetch_api_3():
    """Simulates fetching data from API 3"""
    await asyncio.sleep(0.8)
    return {"source": "API 3", "data": "Payment methods"}


@app.get("/parallel/gather")
async def parallel_gather_demo():
    """
    Demonstrates asyncio.gather() for parallel execution.
    
    All operations run concurrently. Total time = max(individual times),
    not sum of all times!
    """
    start = time.time()
    
    # Run all three API calls concurrently
    result1, result2, result3 = await asyncio.gather(
        fetch_api_1(),
        fetch_api_2(),
        fetch_api_3()
    )
    
    duration = time.time() - start
    
    return {
        "results": [result1, result2, result3],
        "total_time": round(duration, 2),
        "sequential_would_take": "3.3 seconds",
        "actual_time": f"{round(duration, 2)} seconds (fastest = 1.5s)",
        "speedup": f"{round(3.3 / duration, 1)}x faster"
    }


@app.get("/parallel/gather-dict")
async def parallel_gather_dict():
    """
    Using asyncio.gather() with dictionary unpacking for cleaner code.
    """
    start = time.time()
    
    # Named results for clarity
    tasks = {
        "user": fetch_api_1(),
        "orders": fetch_api_2(),
        "payments": fetch_api_3()
    }
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks.values())
    
    # Combine with keys
    combined = dict(zip(tasks.keys(), results))
    
    duration = time.time() - start
    
    return {
        "data": combined,
        "execution_time": round(duration, 2),
        "note": "All operations ran in parallel"
    }


# ============================================================================
# SECTION 2: Error Handling in Concurrent Operations
# ============================================================================

async def task_success():
    await asyncio.sleep(0.5)
    return {"status": "success", "data": "Task completed"}


async def task_failure():
    await asyncio.sleep(0.3)
    raise ValueError("Task failed intentionally")


async def task_slow():
    await asyncio.sleep(2)
    return {"status": "success", "data": "Slow task completed"}


@app.get("/error-handling/default")
async def error_handling_default():
    """
    By default, asyncio.gather() raises exception and cancels other tasks
    if any task fails.
    """
    try:
        start = time.time()
        results = await asyncio.gather(
            task_success(),
            task_failure(),  # This will raise an exception
            task_slow()
        )
        return {"results": results}
    except ValueError as e:
        duration = time.time() - start
        return {
            "error": str(e),
            "message": "One task failed, all tasks stopped",
            "execution_time": round(duration, 2),
            "note": "Default behavior: first exception stops everything"
        }


@app.get("/error-handling/return-exceptions")
async def error_handling_return_exceptions():
    """
    With return_exceptions=True, gather() returns exceptions instead of raising.
    All tasks complete even if some fail.
    """
    start = time.time()
    
    results = await asyncio.gather(
        task_success(),
        task_failure(),
        task_slow(),
        return_exceptions=True  # Don't raise, return exceptions
    )
    
    duration = time.time() - start
    
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "task": i + 1,
                "status": "failed",
                "error": str(result)
            })
        else:
            processed_results.append({
                "task": i + 1,
                "status": "success",
                "data": result
            })
    
    return {
        "results": processed_results,
        "execution_time": round(duration, 2),
        "note": "All tasks completed despite one failing"
    }


# ============================================================================
# SECTION 3: Timeouts with asyncio.wait_for()
# ============================================================================

async def slow_operation():
    """Simulates a slow operation that might timeout"""
    await asyncio.sleep(5)
    return {"data": "Operation completed"}


@app.get("/timeout/basic")
async def timeout_basic():
    """
    Demonstrates timeout handling with asyncio.wait_for()
    """
    try:
        start = time.time()
        
        # Wait maximum 2 seconds
        result = await asyncio.wait_for(
            slow_operation(),
            timeout=2.0
        )
        
        return result
        
    except asyncio.TimeoutError:
        duration = time.time() - start
        return {
            "error": "Operation timed out",
            "timeout": "2 seconds",
            "elapsed": round(duration, 2),
            "message": "Operation was cancelled after timeout"
        }


@app.get("/timeout/multiple-with-fallback")
async def timeout_multiple_with_fallback():
    """
    Multiple operations with timeouts and fallback values
    """
    async def safe_fetch(operation, timeout: float, fallback):
        try:
            return await asyncio.wait_for(operation, timeout=timeout)
        except asyncio.TimeoutError:
            return fallback
    
    start = time.time()
    
    # Run multiple operations with different timeouts
    results = await asyncio.gather(
        safe_fetch(fetch_api_1(), timeout=2.0, fallback={"error": "timeout", "source": "API 1"}),
        safe_fetch(fetch_api_2(), timeout=2.0, fallback={"error": "timeout", "source": "API 2"}),
        safe_fetch(slow_operation(), timeout=1.0, fallback={"error": "timeout", "source": "Slow API"}),
    )
    
    duration = time.time() - start
    
    return {
        "results": results,
        "execution_time": round(duration, 2),
        "note": "Operations with timeout returned fallback values"
    }


# ============================================================================
# SECTION 4: Rate Limiting with Semaphores
# ============================================================================

# Limit to 3 concurrent operations
rate_limiter = asyncio.Semaphore(3)


async def rate_limited_task(task_id: int):
    """
    Task that uses semaphore for rate limiting.
    Only 3 of these can run simultaneously.
    """
    async with rate_limiter:
        print(f"Task {task_id} started at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        await asyncio.sleep(1)
        print(f"Task {task_id} finished at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        return f"Task {task_id} completed"


@app.get("/rate-limiting/semaphore")
async def rate_limiting_semaphore():
    """
    Demonstrates rate limiting with semaphores.
    
    Even though we start 10 tasks, only 3 run at a time.
    """
    start = time.time()
    
    # Start 10 tasks, but only 3 can run concurrently
    tasks = [rate_limited_task(i) for i in range(1, 11)]
    results = await asyncio.gather(*tasks)
    
    duration = time.time() - start
    
    return {
        "results": results,
        "total_tasks": len(results),
        "concurrent_limit": 3,
        "execution_time": round(duration, 2),
        "expected_time": "~4 seconds (10 tasks / 3 concurrent, each taking 1s)",
        "note": "Semaphore limited concurrency to 3 tasks at a time"
    }


# Simulate API rate limiting
api_semaphore = asyncio.Semaphore(5)


async def call_external_api(url: str):
    """Simulates calling external API with rate limiting"""
    async with api_semaphore:
        await asyncio.sleep(0.5)
        return {"url": url, "status": "success"}


@app.get("/rate-limiting/api-calls")
async def rate_limiting_api_calls():
    """
    Practical example: Rate limiting external API calls.
    
    Useful when external APIs have rate limits.
    """
    urls = [f"https://api.example.com/endpoint/{i}" for i in range(20)]
    
    start = time.time()
    results = await asyncio.gather(*[call_external_api(url) for url in urls])
    duration = time.time() - start
    
    return {
        "total_requests": len(results),
        "concurrent_limit": 5,
        "execution_time": round(duration, 2),
        "requests_per_second": round(len(results) / duration, 1),
        "note": "Rate limiting prevents overwhelming external APIs"
    }


# ============================================================================
# SECTION 5: Task Management
# ============================================================================

# Store background tasks
background_tasks: Dict[str, asyncio.Task] = {}


async def long_running_task(task_id: str, duration: int):
    """Simulates a long-running background task"""
    try:
        for i in range(duration):
            await asyncio.sleep(1)
            print(f"Task {task_id}: {i + 1}/{duration} seconds")
        return {"task_id": task_id, "status": "completed", "duration": duration}
    except asyncio.CancelledError:
        print(f"Task {task_id} was cancelled")
        raise


@app.post("/tasks/create/{task_id}")
async def create_background_task(task_id: str, duration: int = 10):
    """
    Create a background task that runs independently.
    
    Task continues running even after response is sent.
    """
    if task_id in background_tasks:
        raise HTTPException(status_code=400, detail="Task ID already exists")
    
    # Create task without awaiting it
    task = asyncio.create_task(long_running_task(task_id, duration))
    background_tasks[task_id] = task
    
    return {
        "message": "Background task created",
        "task_id": task_id,
        "duration": duration,
        "note": "Task is running in the background"
    }


@app.get("/tasks/status/{task_id}")
async def get_task_status(task_id: str):
    """Check the status of a background task"""
    if task_id not in background_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = background_tasks[task_id]
    
    if task.done():
        try:
            result = task.result()
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result
            }
        except asyncio.CancelledError:
            return {
                "task_id": task_id,
                "status": "cancelled"
            }
        except Exception as e:
            return {
                "task_id": task_id,
                "status": "failed",
                "error": str(e)
            }
    else:
        return {
            "task_id": task_id,
            "status": "running"
        }


@app.delete("/tasks/cancel/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a running background task"""
    if task_id not in background_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = background_tasks[task_id]
    
    if task.done():
        return {
            "message": "Task already completed",
            "task_id": task_id
        }
    
    # Cancel the task
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    del background_tasks[task_id]
    
    return {
        "message": "Task cancelled successfully",
        "task_id": task_id
    }


@app.get("/tasks/list")
async def list_tasks():
    """List all background tasks and their statuses"""
    tasks_info = []
    
    for task_id, task in background_tasks.items():
        if task.done():
            status = "completed"
        else:
            status = "running"
        
        tasks_info.append({
            "task_id": task_id,
            "status": status
        })
    
    return {
        "tasks": tasks_info,
        "total": len(tasks_info)
    }


# ============================================================================
# SECTION 6: Real-World Example - Data Aggregation
# ============================================================================

async def fetch_weather(city: str):
    """Simulate fetching weather data"""
    await asyncio.sleep(0.5)
    return {
        "city": city,
        "temperature": 20 + hash(city) % 15,
        "condition": "Sunny"
    }


async def fetch_news(city: str):
    """Simulate fetching news"""
    await asyncio.sleep(0.8)
    return {
        "city": city,
        "headlines": [f"Breaking news in {city}", f"Local events in {city}"]
    }


async def fetch_traffic(city: str):
    """Simulate fetching traffic data"""
    await asyncio.sleep(0.3)
    return {
        "city": city,
        "traffic_level": "moderate",
        "delays": "10 minutes average"
    }


@app.get("/aggregate/city-info/{city}")
async def aggregate_city_info(city: str):
    """
    Real-world example: Aggregate data from multiple sources.
    
    This pattern is common in microservices architectures.
    """
    start = time.time()
    
    try:
        # Fetch all data concurrently with timeout
        weather, news, traffic = await asyncio.gather(
            asyncio.wait_for(fetch_weather(city), timeout=2.0),
            asyncio.wait_for(fetch_news(city), timeout=2.0),
            asyncio.wait_for(fetch_traffic(city), timeout=2.0),
            return_exceptions=True
        )
        
        duration = time.time() - start
        
        # Process results
        result = {"city": city}
        
        if isinstance(weather, Exception):
            result["weather"] = {"error": "Failed to fetch"}
        else:
            result["weather"] = weather
        
        if isinstance(news, Exception):
            result["news"] = {"error": "Failed to fetch"}
        else:
            result["news"] = news
        
        if isinstance(traffic, Exception):
            result["traffic"] = {"error": "Failed to fetch"}
        else:
            result["traffic"] = traffic
        
        result["fetch_time"] = round(duration, 2)
        result["note"] = "All sources queried concurrently"
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SECTION 7: Best Practices Summary
# ============================================================================

@app.get("/best-practices")
async def concurrency_best_practices():
    """Concurrency patterns best practices"""
    return {
        "parallel_execution": {
            "use": "asyncio.gather() for running multiple operations concurrently",
            "benefit": "Reduces total execution time to max(operations) instead of sum(operations)",
            "example": "Fetching data from multiple APIs or databases"
        },
        "error_handling": {
            "default": "gather() stops all tasks on first exception",
            "return_exceptions": "Use return_exceptions=True to continue despite failures",
            "recommendation": "Always handle exceptions in production code"
        },
        "timeouts": {
            "use": "asyncio.wait_for() to prevent hanging operations",
            "critical_for": ["External API calls", "Database queries", "File operations"],
            "pattern": "try/except asyncio.TimeoutError with fallback values"
        },
        "rate_limiting": {
            "use": "asyncio.Semaphore() to limit concurrent operations",
            "critical_for": ["External API rate limits", "Database connection limits", "Resource constraints"],
            "example": "Limit to N concurrent database queries or API calls"
        },
        "background_tasks": {
            "use": "asyncio.create_task() for fire-and-forget operations",
            "critical_for": ["Logging", "Cache warming", "Async notifications"],
            "warning": "Track tasks if you need to cancel or get results later"
        },
        "common_patterns": {
            "fan_out_fan_in": "Distribute work, gather results (asyncio.gather)",
            "timeout_fallback": "Try operation with timeout, use fallback on timeout",
            "retry_pattern": "Retry failed operations with exponential backoff",
            "circuit_breaker": "Stop calling failing services temporarily"
        }
    }


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "title": "Concurrency Patterns API",
        "description": "Learn advanced concurrency patterns in FastAPI",
        "patterns": {
            "parallel_execution": "/parallel/gather",
            "error_handling": "/error-handling/return-exceptions",
            "timeouts": "/timeout/basic",
            "rate_limiting": "/rate-limiting/semaphore",
            "background_tasks": "POST /tasks/create/{task_id}",
            "data_aggregation": "/aggregate/city-info/NewYork",
            "best_practices": "/best-practices"
        },
        "interactive_demo": {
            "create_task": "POST /tasks/create/my-task?duration=10",
            "check_status": "GET /tasks/status/my-task",
            "cancel_task": "DELETE /tasks/cancel/my-task",
            "list_tasks": "GET /tasks/list"
        },
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("🚀 Starting Concurrency Patterns API")
    print("="*70)
    print("\nPatterns demonstrated:")
    print("  • Parallel execution with asyncio.gather()")
    print("  • Error handling in concurrent operations")
    print("  • Timeouts with asyncio.wait_for()")
    print("  • Rate limiting with Semaphores")
    print("  • Background task management")
    print("\nTry:")
    print("  • http://localhost:8002/docs")
    print("  • http://localhost:8002/parallel/gather")
    print("  • http://localhost:8002/rate-limiting/semaphore")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
