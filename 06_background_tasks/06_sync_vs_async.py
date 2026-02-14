"""
Sync vs Async Background Tasks - Performance Comparison
========================================================

This module demonstrates the performance difference between
synchronous and asynchronous background tasks.
"""

from fastapi import FastAPI, BackgroundTasks
import time
import asyncio
from datetime import datetime
from typing import List

app = FastAPI(title="Sync vs Async Comparison")

# Tracking
execution_log = []

# ========================================
# Synchronous Tasks
# ========================================

def sync_task_short(task_id: int):
    """Sync task - 1 second"""
    start = time.time()
    time.sleep(1)  # Blocking!
    duration = time.time() - start
    
    log = {
        "task_id": task_id,
        "type": "sync",
        "duration": f"{duration:.2f}s",
        "timestamp": datetime.now().isoformat()
    }
    execution_log.append(log)
    print(f"✅ Sync Task {task_id} completed in {duration:.2f}s")

def sync_task_medium(task_id: int):
    """Sync task - 2 seconds"""
    start = time.time()
    time.sleep(2)
    duration = time.time() - start
    
    log = {
        "task_id": task_id,
        "type": "sync",
        "duration": f"{duration:.2f}s",
        "timestamp": datetime.now().isoformat()
    }
    execution_log.append(log)
    print(f"✅ Sync Task {task_id} completed in {duration:.2f}s")

def sync_task_long(task_id: int):
    """Sync task - 3 seconds"""
    start = time.time()
    time.sleep(3)
    duration = time.time() - start
    
    log = {
        "task_id": task_id,
        "type": "sync",
        "duration": f"{duration:.2f}s",
        "timestamp": datetime.now().isoformat()
    }
    execution_log.append(log)
    print(f"✅ Sync Task {task_id} completed in {duration:.2f}s")

# ========================================
# Asynchronous Tasks
# ========================================

async def async_task_short(task_id: int):
    """Async task - 1 second"""
    start = time.time()
    await asyncio.sleep(1)  # Non-blocking!
    duration = time.time() - start
    
    log = {
        "task_id": task_id,
        "type": "async",
        "duration": f"{duration:.2f}s",
        "timestamp": datetime.now().isoformat()
    }
    execution_log.append(log)
    print(f"✅ Async Task {task_id} completed in {duration:.2f}s")

async def async_task_medium(task_id: int):
    """Async task - 2 seconds"""
    start = time.time()
    await asyncio.sleep(2)
    duration = time.time() - start
    
    log = {
        "task_id": task_id,
        "type": "async",
        "duration": f"{duration:.2f}s",
        "timestamp": datetime.now().isoformat()
    }
    execution_log.append(log)
    print(f"✅ Async Task {task_id} completed in {duration:.2f}s")

async def async_task_long(task_id: int):
    """Async task - 3 seconds"""
    start = time.time()
    await asyncio.sleep(3)
    duration = time.time() - start
    
    log = {
        "task_id": task_id,
        "type": "async",
        "duration": f"{duration:.2f}s",
        "timestamp": datetime.now().isoformat()
    }
    execution_log.append(log)
    print(f"✅ Async Task {task_id} completed in {duration:.2f}s")

# ========================================
# Comparison Endpoints
# ========================================

@app.post("/compare/sequential-sync")
async def sequential_sync(background_tasks: BackgroundTasks):
    """
    Sequential sync tasks
    
    3 tasks × 2 seconds each = ~6 seconds total
    Tasks run one after another (blocking)
    """
    background_tasks.add_task(sync_task_medium, 1)
    background_tasks.add_task(sync_task_medium, 2)
    background_tasks.add_task(sync_task_medium, 3)
    
    return {
        "message": "3 sync tasks queued",
        "expected_time": "~6 seconds (sequential)",
        "note": "Each task blocks the next one"
    }

@app.post("/compare/sequential-async")
async def sequential_async(background_tasks: BackgroundTasks):
    """
    Sequential async tasks
    
    3 tasks × 2 seconds each = ~2 seconds total (concurrent!)
    Tasks can run concurrently during I/O waits
    """
    background_tasks.add_task(async_task_medium, 1)
    background_tasks.add_task(async_task_medium, 2)
    background_tasks.add_task(async_task_medium, 3)
    
    return {
        "message": "3 async tasks queued",
        "expected_time": "~2 seconds (concurrent)",
        "note": "Tasks can overlap during I/O waits"
    }

@app.post("/compare/many-sync")
async def many_sync(background_tasks: BackgroundTasks):
    """
    Many sync tasks
    
    10 tasks × 1 second each = ~10 seconds total
    """
    for i in range(1, 11):
        background_tasks.add_task(sync_task_short, i)
    
    return {
        "message": "10 sync tasks queued",
        "expected_time": "~10 seconds (sequential)",
        "note": "Watch them execute one by one"
    }

@app.post("/compare/many-async")
async def many_async(background_tasks: BackgroundTasks):
    """
    Many async tasks
    
    10 tasks × 1 second each = ~1 second total (concurrent!)
    """
    for i in range(1, 11):
        background_tasks.add_task(async_task_short, i)
    
    return {
        "message": "10 async tasks queued",
        "expected_time": "~1 second (concurrent)",
        "note": "Watch them execute together!"
    }

@app.post("/compare/mixed")
async def mixed_tasks(background_tasks: BackgroundTasks):
    """
    Mixed sync and async tasks
    
    Demonstrates how they interact
    """
    background_tasks.add_task(sync_task_short, 1)
    background_tasks.add_task(async_task_short, 2)
    background_tasks.add_task(sync_task_short, 3)
    background_tasks.add_task(async_task_short, 4)
    
    return {
        "message": "4 mixed tasks queued",
        "note": "Async tasks can overlap, sync tasks block"
    }

# ========================================
# Real-World Simulation
# ========================================

def sync_database_query():
    """Simulates blocking database query"""
    time.sleep(2)
    print("📊 Sync DB query completed")

async def async_database_query():
    """Simulates non-blocking database query"""
    await asyncio.sleep(2)
    print("📊 Async DB query completed")

def sync_api_call():
    """Simulates blocking HTTP request"""
    time.sleep(1.5)
    print("🌐 Sync API call completed")

async def async_api_call():
    """Simulates non-blocking HTTP request"""
    await asyncio.sleep(1.5)
    print("🌐 Async API call completed")

@app.post("/real-world/sync")
async def real_world_sync(background_tasks: BackgroundTasks):
    """
    Real-world scenario with sync tasks
    
    - Database query (2s)
    - API call (1.5s)
    - Another DB query (2s)
    
    Total: ~5.5 seconds
    """
    background_tasks.add_task(sync_database_query)
    background_tasks.add_task(sync_api_call)
    background_tasks.add_task(sync_database_query)
    
    return {
        "message": "Real-world sync tasks queued",
        "expected_time": "~5.5 seconds",
        "tasks": ["DB query", "API call", "DB query"]
    }

@app.post("/real-world/async")
async def real_world_async(background_tasks: BackgroundTasks):
    """
    Real-world scenario with async tasks
    
    - Database query (2s)
    - API call (1.5s)
    - Another DB query (2s)
    
    Total: ~2 seconds (concurrent!)
    """
    background_tasks.add_task(async_database_query)
    background_tasks.add_task(async_api_call)
    background_tasks.add_task(async_database_query)
    
    return {
        "message": "Real-world async tasks queued",
        "expected_time": "~2 seconds",
        "tasks": ["DB query (async)", "API call (async)", "DB query (async)"],
        "note": "All run concurrently!"
    }

# ========================================
# Utility Endpoints
# ========================================

@app.get("/logs")
async def get_logs():
    """Get execution logs"""
    return {
        "total_tasks": len(execution_log),
        "logs": execution_log
    }

@app.delete("/logs")
async def clear_logs():
    """Clear execution logs"""
    execution_log.clear()
    return {"message": "Logs cleared"}

@app.get("/logs/analysis")
async def analyze_logs():
    """Analyze execution patterns"""
    if not execution_log:
        return {"message": "No logs available"}
    
    sync_tasks = [log for log in execution_log if log["type"] == "sync"]
    async_tasks = [log for log in execution_log if log["type"] == "async"]
    
    return {
        "total_tasks": len(execution_log),
        "sync_tasks": len(sync_tasks),
        "async_tasks": len(async_tasks),
        "logs": execution_log
    }

@app.get("/")
async def root():
    return {
        "message": "Sync vs Async Performance Comparison",
        "endpoints": {
            "sequential_sync": "POST /compare/sequential-sync",
            "sequential_async": "POST /compare/sequential-async",
            "many_sync": "POST /compare/many-sync",
            "many_async": "POST /compare/many-async",
            "mixed": "POST /compare/mixed",
            "real_world_sync": "POST /real-world/sync",
            "real_world_async": "POST /real-world/async",
            "logs": "GET /logs",
            "analysis": "GET /logs/analysis"
        },
        "key_differences": {
            "sync": "Tasks run one after another (blocking)",
            "async": "Tasks can run concurrently during I/O waits"
        },
        "recommendation": "Use async for I/O-bound operations (DB, API, files)"
    }

# ========================================
# Run the app
# ========================================
if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("  Sync vs Async Background Tasks Comparison")
    print("="*60)
    print("\nStarting server on http://localhost:8002")
    print("\nTest it:")
    print("  1. Open http://localhost:8002/docs")
    print("  2. Try the comparison endpoints")
    print("  3. Watch the console for execution logs")
    print("  4. Check /logs to see execution times")
    print("\nKey Difference:")
    print("  • Sync tasks: Run sequentially (one after another)")
    print("  • Async tasks: Can run concurrently (overlap during I/O)")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
