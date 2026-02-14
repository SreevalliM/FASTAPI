# 10. Writing Scalable APIs with FastAPI

## Table of Contents
1. [Introduction](#introduction)
2. [async def vs def](#async-def-vs-def)
3. [Event Loop Basics](#event-loop-basics)
4. [Async DB Drivers](#async-db-drivers)
5. [Concurrency Patterns](#concurrency-patterns)
6. [ASGI vs WSGI](#asgi-vs-wsgi)
7. [Uvicorn & Gunicorn Workers](#uvicorn--gunicorn-workers)
8. [When to Use Async](#when-to-use-async)
9. [Performance Best Practices](#performance-best-practices)
10. [Production Deployment](#production-deployment)

---

## Introduction

Scalability is critical for modern APIs. FastAPI, built on ASGI (Asynchronous Server Gateway Interface), provides excellent support for async operations, enabling your API to handle thousands of concurrent requests efficiently.

**Key Benefits of Async APIs:**
- Handle more concurrent requests with fewer resources
- Better I/O-bound operation performance (DB queries, API calls, file operations)
- Reduced latency for users
- Cost-effective scaling

---

## async def vs def

### Understanding the Difference

```python
from fastapi import FastAPI
import time
import asyncio

app = FastAPI()

# Synchronous endpoint
@app.get("/sync")
def sync_endpoint():
    """Blocks the event loop during execution"""
    time.sleep(1)  # Simulates blocking I/O
    return {"message": "Sync operation complete"}

# Asynchronous endpoint
@app.get("/async")
async def async_endpoint():
    """Yields control back to the event loop"""
    await asyncio.sleep(1)  # Non-blocking wait
    return {"message": "Async operation complete"}
```

### Key Differences

| Aspect | `def` (Sync) | `async def` (Async) |
|--------|--------------|---------------------|
| **Execution** | Runs in thread pool | Runs in event loop |
| **Blocking** | Blocks during I/O | Non-blocking I/O |
| **Concurrency** | Limited by thread pool | High concurrency |
| **Use Case** | CPU-bound tasks | I/O-bound tasks |
| **await keyword** | ❌ Cannot use | ✅ Must use for async ops |

### What Happens Under the Hood

**Synchronous (`def`):**
```python
@app.get("/sync-operation")
def sync_operation():
    # FastAPI runs this in a ThreadPoolExecutor
    # Each request consumes a thread
    # Thread is blocked during the entire execution
    result = blocking_database_query()  # Blocks the thread
    return result
```

**Asynchronous (`async def`):**
```python
@app.get("/async-operation")
async def async_operation():
    # Runs in the event loop
    # During await, the event loop can handle other requests
    result = await async_database_query()  # Yields control
    return result
```

### Performance Example

```python
import asyncio
import time
from fastapi import FastAPI

app = FastAPI()

# This will handle ~10 requests/second (with 1s sleep)
@app.get("/slow-sync")
def slow_sync():
    time.sleep(1)
    return {"status": "done"}

# This can handle thousands of requests/second concurrently
@app.get("/fast-async")
async def fast_async():
    await asyncio.sleep(1)
    return {"status": "done"}
```

---

## Event Loop Basics

### What is the Event Loop?

The event loop is the core of async programming. It manages and executes async tasks, handling I/O operations without blocking.

```
┌───────────────────────────┐
│   Event Loop               │
│                            │
│  ┌──────────────────────┐ │
│  │  Task Queue           │ │
│  │  - Task 1 (waiting)   │ │
│  │  - Task 2 (ready)     │ │
│  │  - Task 3 (running)   │ │
│  └──────────────────────┘ │
│                            │
│  When task awaits I/O,    │
│  loop switches to another │
│  task immediately         │
└───────────────────────────┘
```

### Event Loop Flow

```python
import asyncio

async def task_a():
    print("Task A: Starting")
    await asyncio.sleep(1)  # Yields control here
    print("Task A: Finished")

async def task_b():
    print("Task B: Starting")
    await asyncio.sleep(0.5)  # Yields control here
    print("Task B: Finished")

async def main():
    # Both tasks run concurrently
    await asyncio.gather(task_a(), task_b())

# Output:
# Task A: Starting
# Task B: Starting
# Task B: Finished (after 0.5s)
# Task A: Finished (after 1s)
```

### Event Loop Lifecycle

```python
import asyncio

# Get the current event loop (FastAPI manages this for you)
loop = asyncio.get_event_loop()

# Run until a coroutine completes
loop.run_until_complete(some_async_function())

# Run forever (for long-running services)
loop.run_forever()

# Close the loop
loop.close()
```

### Important Concepts

**1. Coroutines:** Functions defined with `async def`
```python
async def my_coroutine():
    await some_async_operation()
```

**2. Tasks:** Scheduled coroutines in the event loop
```python
task = asyncio.create_task(my_coroutine())
```

**3. Futures:** Objects representing the eventual result of an async operation
```python
future = asyncio.ensure_future(my_coroutine())
```

---

## Async DB Drivers

### Why Async Database Drivers?

Traditional database drivers (like `psycopg2`, `pymysql`) are **blocking** - they freeze your entire async application while waiting for database responses.

**Problem with Blocking Drivers:**
```python
# ❌ Bad: Blocks the event loop
async def get_user(user_id: int):
    # Using psycopg2 (blocking driver)
    result = cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    # Event loop is blocked, can't handle other requests!
    return result
```

**Solution with Async Drivers:**
```python
# ✅ Good: Non-blocking
async def get_user(user_id: int):
    # Using asyncpg (async driver)
    result = await conn.fetch("SELECT * FROM users WHERE id = $1", user_id)
    # During await, event loop handles other requests
    return result
```

### Popular Async Database Drivers

| Database | Sync Driver | Async Driver | ORM Support |
|----------|-------------|--------------|-------------|
| **PostgreSQL** | psycopg2 | asyncpg | SQLAlchemy (async) |
| **MySQL** | pymysql | aiomysql | SQLAlchemy (async) |
| **MongoDB** | pymongo | motor | ODMantic, Beanie |
| **Redis** | redis-py | aioredis | - |
| **SQLite** | sqlite3 | aiosqlite | SQLAlchemy (async) |

### PostgreSQL with asyncpg

```python
import asyncpg
from fastapi import FastAPI

app = FastAPI()

# Connection pool (reuse connections)
db_pool = None

@app.on_event("startup")
async def startup():
    global db_pool
    db_pool = await asyncpg.create_pool(
        host="localhost",
        database="mydb",
        user="user",
        password="password",
        min_size=10,
        max_size=20
    )

@app.on_event("shutdown")
async def shutdown():
    await db_pool.close()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    async with db_pool.acquire() as conn:
        # Execute query asynchronously
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE id = $1", 
            user_id
        )
        return dict(user) if user else None
```

### SQLAlchemy 2.0 Async

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Create async engine
engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/dbname",
    echo=True,
    pool_size=10,
    max_overflow=20
)

# Create async session maker
async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Define model
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]

# Use in FastAPI
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        return user
```

### MongoDB with Motor

```python
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI

app = FastAPI()
mongodb_client = None
database = None

@app.on_event("startup")
async def startup():
    global mongodb_client, database
    mongodb_client = AsyncIOMotorClient("mongodb://localhost:27017")
    database = mongodb_client.mydb

@app.on_event("shutdown")
async def shutdown():
    mongodb_client.close()

@app.get("/products/{product_id}")
async def get_product(product_id: str):
    product = await database.products.find_one({"_id": product_id})
    return product
```

### Connection Pooling Best Practices

```python
# ✅ Good: Use connection pooling
db_pool = await asyncpg.create_pool(
    dsn="postgresql://...",
    min_size=10,      # Minimum connections in pool
    max_size=20,      # Maximum connections in pool
    max_queries=50000, # Recycle connection after N queries
    max_inactive_connection_lifetime=300  # 5 minutes
)

# ❌ Bad: Creating new connection per request
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # This is inefficient!
    conn = await asyncpg.connect(dsn="postgresql://...")
    user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    await conn.close()
    return user
```

---

## Concurrency Patterns

### 1. Parallel Async Operations with `asyncio.gather()`

Execute multiple async operations concurrently:

```python
import asyncio
from fastapi import FastAPI

app = FastAPI()

async def fetch_user(user_id: int):
    await asyncio.sleep(0.1)  # Simulate DB query
    return {"id": user_id, "name": f"User {user_id}"}

async def fetch_orders(user_id: int):
    await asyncio.sleep(0.1)  # Simulate DB query
    return [{"id": 1, "total": 100}, {"id": 2, "total": 200}]

async def fetch_profile(user_id: int):
    await asyncio.sleep(0.1)  # Simulate DB query
    return {"bio": "Software Developer"}

@app.get("/user-dashboard/{user_id}")
async def get_user_dashboard(user_id: int):
    # Run all three queries concurrently (0.1s total instead of 0.3s)
    user, orders, profile = await asyncio.gather(
        fetch_user(user_id),
        fetch_orders(user_id),
        fetch_profile(user_id)
    )
    
    return {
        "user": user,
        "orders": orders,
        "profile": profile
    }
```

### 2. Concurrent Requests with Timeout

```python
import asyncio
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/data-with-timeout")
async def get_data_with_timeout():
    try:
        # Wait maximum 5 seconds
        result = await asyncio.wait_for(
            slow_database_query(),
            timeout=5.0
        )
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Database timeout")
```

### 3. Semaphore for Rate Limiting

```python
import asyncio

# Limit to 5 concurrent database connections
db_semaphore = asyncio.Semaphore(5)

async def query_database(query: str):
    async with db_semaphore:
        # Only 5 of these can run simultaneously
        await asyncio.sleep(0.5)
        return {"result": "data"}

@app.get("/limited-endpoint")
async def limited_endpoint():
    result = await query_database("SELECT * FROM table")
    return result
```

### 4. Task Groups (Python 3.11+)

```python
import asyncio

@app.get("/process-batch")
async def process_batch():
    async with asyncio.TaskGroup() as group:
        task1 = group.create_task(process_item(1))
        task2 = group.create_task(process_item(2))
        task3 = group.create_task(process_item(3))
    
    # All tasks completed or one raised an exception
    return {"status": "all processed"}
```

### 5. Background Processing with asyncio.create_task()

```python
import asyncio
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

async def send_email(email: str, message: str):
    await asyncio.sleep(2)  # Simulate email sending
    print(f"Email sent to {email}")

@app.post("/register")
async def register(email: str):
    # Don't wait for email to be sent
    asyncio.create_task(send_email(email, "Welcome!"))
    
    # Return immediately
    return {"message": "Registration successful"}
```

---

## ASGI vs WSGI

### What is WSGI?

**WSGI (Web Server Gateway Interface)** is a synchronous interface between web servers and Python web applications.

```python
# WSGI application (Flask, Django)
def application(environ, start_response):
    # Synchronous, blocking
    status = '200 OK'
    headers = [('Content-Type', 'text/plain')]
    start_response(status, headers)
    return [b'Hello World']
```

**Characteristics:**
- ✅ Mature, well-established standard
- ✅ Wide ecosystem support
- ❌ Synchronous only (one request per thread)
- ❌ Cannot handle websockets natively
- ❌ Higher resource consumption under high concurrency

### What is ASGI?

**ASGI (Asynchronous Server Gateway Interface)** is the async successor to WSGI, designed for modern async Python frameworks.

```python
# ASGI application (FastAPI, Starlette)
async def application(scope, receive, send):
    # Asynchronous, non-blocking
    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [[b'content-type', b'text/plain']],
    })
    await send({
        'type': 'http.response.body',
        'body': b'Hello World',
    })
```

**Characteristics:**
- ✅ Asynchronous, high concurrency
- ✅ Supports WebSockets, HTTP/2, Server-Sent Events
- ✅ Better resource utilization
- ✅ Lower latency
- ⚠️ Requires async-compatible libraries

### Comparison Table

| Feature | WSGI | ASGI |
|---------|------|------|
| **Async Support** | ❌ No | ✅ Yes |
| **WebSockets** | ❌ No | ✅ Yes |
| **HTTP/2** | Limited | ✅ Yes |
| **Server-Sent Events** | Difficult | ✅ Yes |
| **Concurrency Model** | Thread-based | Event loop |
| **Memory Usage (1000 req)** | ~100 MB | ~20 MB |
| **Throughput** | Lower | Higher |
| **Frameworks** | Flask, Django | FastAPI, Starlette |
| **Servers** | Gunicorn, uWSGI | Uvicorn, Hypercorn, Daphne |

### Real-World Performance Comparison

**WSGI (Flask with Gunicorn):**
```python
# Flask app (WSGI)
from flask import Flask
app = Flask(__name__)

@app.route('/api/users')
def get_users():
    # Each request blocks a thread
    users = db.query("SELECT * FROM users")  # Blocking
    return jsonify(users)

# Run with: gunicorn -w 4 app:app
# 4 worker processes, ~30 threads each = ~120 concurrent requests max
```

**ASGI (FastAPI with Uvicorn):**
```python
# FastAPI app (ASGI)
from fastapi import FastAPI
app = FastAPI()

@app.get('/api/users')
async def get_users():
    # Non-blocking, thousands of concurrent requests
    users = await db.fetch("SELECT * FROM users")  # Non-blocking
    return users

# Run with: uvicorn app:app --workers 4
# 4 worker processes, thousands of concurrent requests per worker
```

### Migration Path

**Can I use async in WSGI apps?**
```python
# Flask (WSGI) with async views (Flask 2.0+)
from flask import Flask
import asyncio

app = Flask(__name__)

@app.route('/async')
async def async_view():
    # Flask will run this in an event loop per request
    # But it's still running on WSGI (less efficient than ASGI)
    await asyncio.sleep(1)
    return 'Done'
```

**⚠️ Important:** Async in WSGI frameworks is less efficient than native ASGI frameworks because WSGI creates a new event loop for each async request.

**Best Practice:** Use ASGI frameworks (FastAPI) for new async projects.

---

## Uvicorn & Gunicorn Workers

### Uvicorn: ASGI Server

**Uvicorn** is a lightning-fast ASGI server built on uvloop and httptools.

#### Basic Usage

```bash
# Single process
uvicorn main:app --host 0.0.0.0 --port 8000

# With reload (development)
uvicorn main:app --reload

# Multiple workers (production)
uvicorn main:app --workers 4

# With specific event loop (uvloop - faster)
uvicorn main:app --loop uvloop
```

#### Configuration Options

```bash
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info \
  --access-log \
  --proxy-headers \
  --forwarded-allow-ips '*' \
  --timeout-keep-alive 5
```

### Gunicorn with Uvicorn Workers

**Gunicorn** is a mature WSGI server that can manage multiple Uvicorn workers, providing better process management.

#### Why Use Gunicorn + Uvicorn?

- ✅ Better worker management (auto-restart on failure)
- ✅ Graceful reloads
- ✅ More configuration options
- ✅ Battle-tested process management

#### Installation

```bash
pip install gunicorn uvicorn[standard]
```

#### Running with Gunicorn

```bash
# Use uvicorn workers
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 30 \
  --graceful-timeout 10 \
  --keep-alive 5
```

#### Configuration File (gunicorn.conf.py)

```python
# gunicorn.conf.py
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 10000
max_requests_jitter = 1000
timeout = 30
graceful_timeout = 10
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "fastapi_app"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Restart workers after this many requests (helps with memory leaks)
max_requests = 10000
max_requests_jitter = 1000

# Preload app (saves memory, but can't do graceful reloads as easily)
preload_app = True
```

#### Running with Config File

```bash
gunicorn main:app -c gunicorn.conf.py
```

### How Many Workers?

**General Formula:**
```
workers = (2 × CPU_cores) + 1
```

**Example:**
```python
import multiprocessing

# 4 CPU cores → 9 workers
workers = (2 * 4) + 1  # = 9
```

**Considerations:**
- **I/O-bound apps** (most APIs): More workers is better
- **CPU-bound apps**: Don't exceed CPU core count
- **Memory**: Each worker consumes memory (~50-100 MB base)
- **Connections**: Uvicorn can handle 1000s of connections per worker

### Production Deployment Example

```bash
#!/bin/bash
# start_production.sh

# Number of workers
WORKERS=$(( 2 * $(nproc) + 1 ))

# Start with Gunicorn + Uvicorn workers
gunicorn main:app \
  --workers $WORKERS \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 60 \
  --graceful-timeout 30 \
  --keep-alive 5 \
  --max-requests 10000 \
  --max-requests-jitter 1000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  --capture-output \
  --enable-stdio-inheritance
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "60"]
```

### Systemd Service (Linux)

```ini
# /etc/systemd/system/fastapi.service
[Unit]
Description=FastAPI Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/fastapi
Environment="PATH=/opt/fastapi/venv/bin"
ExecStart=/opt/fastapi/venv/bin/gunicorn main:app \
  --workers 9 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable fastapi
sudo systemctl start fastapi

# Check status
sudo systemctl status fastapi

# Reload (graceful restart)
sudo systemctl reload fastapi
```

---

## When to Use Async

### ✅ Use Async When:

#### 1. **I/O-Bound Operations**
```python
# Database queries
async def get_user(user_id: int):
    return await db.fetch_one(f"SELECT * FROM users WHERE id = {user_id}")

# External API calls
async def fetch_external_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()

# File operations
async def read_large_file():
    async with aiofiles.open("large_file.txt", "r") as f:
        contents = await f.read()
        return contents
```

#### 2. **Multiple Concurrent Operations**
```python
# Calling multiple services
async def aggregate_data(user_id: int):
    user, orders, reviews = await asyncio.gather(
        get_user(user_id),
        get_orders(user_id),
        get_reviews(user_id)
    )
    return {"user": user, "orders": orders, "reviews": reviews}
```

#### 3. **High Concurrency Requirements**
```python
# Handling thousands of simultaneous connections
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Echo: {data}")
```

#### 4. **Long-Running Requests**
```python
# Server-sent events, streaming
async def event_stream():
    async for event in monitor_system():
        yield f"data: {event}\n\n"
```

### ❌ Don't Use Async When:

#### 1. **CPU-Bound Operations**
```python
# ❌ Bad: CPU-intensive work blocks event loop
async def calculate_fibonacci(n: int):
    if n <= 1:
        return n
    # This blocks the event loop!
    return await calculate_fibonacci(n-1) + await calculate_fibonacci(n-2)

# ✅ Good: Use regular function and thread pool
def calculate_fibonacci(n: int):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

@app.get("/fib/{n}")
def get_fibonacci(n: int):
    # FastAPI runs this in thread pool automatically
    return {"result": calculate_fibonacci(n)}
```

#### 2. **Simple CRUD Operations (No External I/O)**
```python
# ❌ Unnecessary: No I/O operations
@app.get("/calculate")
async def calculate(a: int, b: int):
    result = a + b  # Pure computation
    return {"result": result}

# ✅ Better: Use regular function
@app.get("/calculate")
def calculate(a: int, b: int):
    result = a + b
    return {"result": result}
```

#### 3. **Using Sync Libraries**
```python
# ❌ Bad: Using blocking library in async function
import requests  # Synchronous library

async def fetch_data():
    # This blocks the event loop!
    response = requests.get("https://api.example.com")
    return response.json()

# ✅ Good: Use async library
import httpx

async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com")
        return response.json()
```

### Decision Matrix

```
┌─────────────────────────────────────┐
│ Does your operation involve I/O?    │
│ (DB, API, files, network)           │
└─────────────┬───────────────────────┘
              │
              ├─── YES ──→ Use async def + await
              │            (Non-blocking I/O)
              │
              └─── NO ───→ Is it CPU-intensive?
                            │
                            ├─── YES ──→ Use def
                            │            (Thread pool)
                            │
                            └─── NO ───→ Either works
                                         (Prefer def for simplicity)
```

### Mixing Async and Sync

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=10)

# Run blocking code in thread pool
@app.get("/mixed")
async def mixed_operation():
    # Async I/O operation
    user = await fetch_user_from_db()
    
    # CPU-bound operation in thread pool
    result = await asyncio.to_thread(cpu_intensive_task, user.data)
    
    # Another async operation
    await send_notification(user.email, result)
    
    return {"result": result}

def cpu_intensive_task(data):
    # Heavy computation
    return sum(i ** 2 for i in range(1000000))
```

---

## Performance Best Practices

### 1. Use Connection Pooling

```python
# ✅ Good: Reuse connections
db_pool = await asyncpg.create_pool(
    dsn="postgresql://...",
    min_size=10,
    max_size=20
)

# ❌ Bad: Create new connection each time
async def query_db():
    conn = await asyncpg.connect(dsn="postgresql://...")
    result = await conn.fetchrow("SELECT * FROM users LIMIT 1")
    await conn.close()
    return result
```

### 2. Avoid Blocking the Event Loop

```python
# ❌ Bad: Blocking operations
import time

@app.get("/blocking")
async def blocking_endpoint():
    time.sleep(5)  # Blocks event loop!
    return {"status": "done"}

# ✅ Good: Use async equivalent
import asyncio

@app.get("/non-blocking")
async def non_blocking_endpoint():
    await asyncio.sleep(5)  # Yields control
    return {"status": "done"}
```

### 3. Set Timeouts

```python
import asyncio

@app.get("/data")
async def get_data():
    try:
        data = await asyncio.wait_for(
            fetch_from_slow_api(),
            timeout=5.0
        )
        return data
    except asyncio.TimeoutError:
        return {"error": "Request timeout"}
```

### 4. Limit Concurrency

```python
# Prevent overwhelming external services
semaphore = asyncio.Semaphore(10)

async def rate_limited_request(url: str):
    async with semaphore:
        async with httpx.AsyncClient() as client:
            return await client.get(url)
```

### 5. Use Caching

```python
from functools import lru_cache
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

@app.get("/expensive-operation")
@cache(expire=3600)  # Cache for 1 hour
async def expensive_operation():
    result = await complex_database_query()
    return result
```

### 6. Optimize Database Queries

```python
# ❌ Bad: N+1 query problem
async def get_users_with_orders():
    users = await db.fetch("SELECT * FROM users")
    for user in users:
        # Separate query for each user!
        user['orders'] = await db.fetch(
            "SELECT * FROM orders WHERE user_id = $1", 
            user['id']
        )
    return users

# ✅ Good: Single query with join
async def get_users_with_orders():
    result = await db.fetch("""
        SELECT u.*, o.id as order_id, o.total
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
    """)
    return result
```

### 7. Monitor Performance

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

---

## Production Deployment

### Complete Production Setup

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="My API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Startup/shutdown events
@app.on_event("startup")
async def startup_event():
    # Initialize database pool
    # Connect to cache
    # Load ML models
    logging.info("Application started")

@app.on_event("shutdown")
async def shutdown_event():
    # Close database connections
    # Close cache connections
    logging.info("Application shutting down")
```

### Docker Setup

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["gunicorn", "main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "60", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/mydb
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
        reservations:
          cpus: '1'
          memory: 512M

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
```

### Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream fastapi {
        server api:8000;
    }

    server {
        listen 80;
        server_name myapi.com;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name myapi.com;

        # SSL certificates
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # Gzip compression
        gzip on;
        gzip_types text/plain text/css application/json application/javascript;

        location / {
            proxy_pass http://fastapi;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # WebSocket support
        location /ws {
            proxy_pass http://fastapi;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi
  template:
    metadata:
      labels:
        app: fastapi
    spec:
      containers:
      - name: fastapi
        image: myregistry/fastapi:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-service
spec:
  selector:
    app: fastapi
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## Summary

### Key Takeaways

1. **async def vs def:**
   - Use `async def` for I/O-bound operations
   - Use `def` for CPU-bound operations
   - FastAPI automatically handles both efficiently

2. **Event Loop:**
   - Core of async programming
   - Allows concurrent execution without threads
   - Never block the event loop with synchronous operations

3. **Async Database Drivers:**
   - Essential for async applications (asyncpg, motor, aiomysql)
   - Always use connection pooling
   - Avoid mixing sync and async database operations

4. **Concurrency:**
   - Use `asyncio.gather()` for parallel operations
   - Implement timeouts and rate limiting
   - Utilize semaphores for resource management

5. **ASGI vs WSGI:**
   - ASGI is superior for modern async applications
   - Supports WebSockets, HTTP/2, and high concurrency
   - FastAPI is built on ASGI

6. **Production Deployment:**
   - Use Gunicorn with Uvicorn workers
   - Calculate workers: (2 × CPU_cores) + 1
   - Implement proper monitoring and logging
   - Use Docker/Kubernetes for scalability

7. **When to Use Async:**
   - ✅ Database queries, API calls, file operations
   - ✅ High concurrency requirements
   - ❌ CPU-intensive computations
   - ❌ When using sync libraries

### Performance Checklist

- [ ] Use connection pooling for databases
- [ ] Implement caching where appropriate
- [ ] Set timeouts on external requests
- [ ] Use async database drivers
- [ ] Optimize database queries (avoid N+1 problems)
- [ ] Implement rate limiting
- [ ] Use compression (GZip middleware)
- [ ] Monitor performance with logging/metrics
- [ ] Deploy with appropriate number of workers
- [ ] Use load balancing (Nginx/cloud load balancer)

---

## Next Steps

1. **Practice:** Implement the example files in this module
2. **Benchmark:** Compare sync vs async performance
3. **Monitor:** Set up logging and metrics in production
4. **Scale:** Deploy with Docker and test under load
5. **Optimize:** Profile your application and identify bottlenecks

Happy building scalable APIs! 🚀
