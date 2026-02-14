# 🚀 Scalable APIs Cheat Sheet

Quick reference for writing scalable FastAPI applications.

---

## 📊 Async def vs def

### When to Use `async def`

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    # ✅ I/O-bound operations
    user = await db.fetch_one("SELECT * FROM users WHERE id = $1", user_id)
    return user
```

**Use for:**
- Database queries (with async drivers)
- External API calls
- File I/O (with aiofiles)
- WebSocket connections
- Any I/O-bound operations

### When to Use `def`

```python
@app.get("/calculate/{n}")
def fibonacci(n: int):
    # ✅ CPU-bound operations
    return calculate_fibonacci(n)
```

**Use for:**
- CPU-intensive calculations
- Data processing
- Using sync libraries (requests, sqlite3)
- Simple operations with no I/O

---

## 🔄 Event Loop Basics

```python
import asyncio

# Get event loop (managed by FastAPI)
loop = asyncio.get_event_loop()

# Run coroutine
result = await some_async_function()

# Run multiple coroutines concurrently
results = await asyncio.gather(
    fetch_user(),
    fetch_orders(),
    fetch_profile()
)

# Create background task
task = asyncio.create_task(background_operation())
```

---

## 💾 Async Database Drivers

### PostgreSQL (asyncpg)

```python
import asyncpg

# Create connection pool
pool = await asyncpg.create_pool(
    "postgresql://user:password@host/db",
    min_size=10,
    max_size=20
)

# Execute query
async with pool.acquire() as conn:
    user = await conn.fetchrow(
        "SELECT * FROM users WHERE id = $1",
        user_id
    )
```

### SQLAlchemy (Async)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Create engine
engine = create_async_engine(
    "postgresql+asyncpg://user:password@host/db",
    pool_size=10
)

# Use session
async with AsyncSession(engine) as session:
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
```

### MongoDB (Motor)

```python
from motor.motor_asyncio import AsyncIOMotorClient

# Create client
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.mydatabase

# Query document
product = await db.products.find_one({"_id": product_id})

# Insert document
result = await db.products.insert_one({
    "name": "Product",
    "price": 99.99
})
```

### SQLite (aiosqlite)

```python
import aiosqlite

# Connect
async with aiosqlite.connect("database.db") as db:
    # Execute query
    async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
        user = await cursor.fetchone()
```

---

## ⚡ Concurrency Patterns

### Parallel Execution

```python
# Run operations concurrently
user, orders, profile = await asyncio.gather(
    fetch_user(user_id),
    fetch_orders(user_id),
    fetch_profile(user_id)
)
```

### Timeout

```python
try:
    result = await asyncio.wait_for(
        slow_operation(),
        timeout=5.0
    )
except asyncio.TimeoutError:
    result = default_value
```

### Rate Limiting with Semaphore

```python
# Limit to 10 concurrent operations
semaphore = asyncio.Semaphore(10)

async def rate_limited_operation():
    async with semaphore:
        return await external_api_call()
```

### Background Tasks

```python
# Fire and forget
task = asyncio.create_task(send_email(user.email))

# Wait for task later
await task

# Cancel task
task.cancel()
```

### Error Handling

```python
# Stop on first exception (default)
results = await asyncio.gather(task1(), task2(), task3())

# Continue despite exceptions
results = await asyncio.gather(
    task1(),
    task2(),
    task3(),
    return_exceptions=True  # Returns exceptions instead of raising
)
```

---

## 🏗️ ASGI vs WSGI

| Feature | WSGI | ASGI |
|---------|------|------|
| **Async Support** | ❌ No | ✅ Yes |
| **WebSockets** | ❌ No | ✅ Yes |
| **HTTP/2** | Limited | ✅ Yes |
| **Concurrency** | Thread-based | Event loop |
| **Frameworks** | Flask, Django | FastAPI, Starlette |
| **Servers** | Gunicorn, uWSGI | Uvicorn, Hypercorn, Daphne |

---

## 🚀 Uvicorn & Gunicorn

### Uvicorn (Development)

```bash
# Single worker
uvicorn main:app --host 0.0.0.0 --port 8000

# With reload
uvicorn main:app --reload

# Multiple workers
uvicorn main:app --workers 4
```

### Gunicorn + Uvicorn (Production)

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 30 \
  --graceful-timeout 10 \
  --keep-alive 5
```

### Worker Calculation

```python
import multiprocessing

# General formula
workers = (2 * multiprocessing.cpu_count()) + 1

# Example: 4 CPU cores → 9 workers
```

### Gunicorn Configuration File

```python
# gunicorn.conf.py
import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 30
graceful_timeout = 10
keepalive = 5
accesslog = "-"
errorlog = "-"
loglevel = "info"
max_requests = 10000
max_requests_jitter = 1000
```

---

## 📈 When to Use Async

### ✅ Use Async When

```
┌─────────────────────────────────────┐
│ I/O-bound operations:               │
├─────────────────────────────────────┤
│ • Database queries                  │
│ • External API calls                │
│ • File operations                   │
│ • WebSockets                        │
│ • High concurrency needed           │
└─────────────────────────────────────┘
```

### ❌ Don't Use Async When

```
┌─────────────────────────────────────┐
│ CPU-bound operations:               │
├─────────────────────────────────────┤
│ • Heavy calculations                │
│ • Data processing                   │
│ • Image/video processing            │
│ • Using sync-only libraries         │
└─────────────────────────────────────┘
```

### Decision Tree

```
Is it I/O-bound? 
├─ YES → Use async def + await
└─ NO → Is it CPU-intensive?
    ├─ YES → Use def (thread pool)
    └─ NO → Use def (simpler)
```

---

## 🎯 Performance Best Practices

### 1. Connection Pooling

```python
# ✅ Good: Reuse connections
pool = await asyncpg.create_pool(
    dsn="postgresql://...",
    min_size=10,
    max_size=20
)

# ❌ Bad: New connection each time
conn = await asyncpg.connect(dsn="postgresql://...")
```

### 2. Concurrent Queries

```python
# ✅ Good: Run concurrently (0.5s total)
user, orders = await asyncio.gather(
    fetch_user(),      # 0.5s
    fetch_orders()     # 0.5s
)

# ❌ Bad: Run sequentially (1.0s total)
user = await fetch_user()      # 0.5s
orders = await fetch_orders()  # 0.5s
```

### 3. Avoid Blocking

```python
# ❌ Bad: Blocks event loop
async def bad():
    time.sleep(1)  # BLOCKS!

# ✅ Good: Non-blocking
async def good():
    await asyncio.sleep(1)  # Yields control
```

### 4. Set Timeouts

```python
# Always set timeouts on external calls
async with httpx.AsyncClient(timeout=5.0) as client:
    response = await client.get(url)
```

### 5. Rate Limiting

```python
# Limit concurrent connections
semaphore = asyncio.Semaphore(10)

async def limited():
    async with semaphore:
        return await operation()
```

---

## 🐳 Production Deployment

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_PASSWORD=secret

  redis:
    image: redis:7-alpine
```

### Kubernetes

```yaml
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
        image: myapp:latest
        ports:
        - containerPort: 8000
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
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
```

---

## 🔍 Health Checks

```python
@app.get("/health")
async def health():
    """Basic health check"""
    return {"status": "healthy"}

@app.get("/health/ready")
async def readiness():
    """Check if ready to receive traffic"""
    db_ready = await check_database()
    return {
        "ready": db_ready,
        "database": "healthy" if db_ready else "unhealthy"
    }

@app.get("/health/live")
async def liveness():
    """Check if process is alive"""
    return {"alive": True}
```

---

## 📊 Monitoring

### Middleware for Metrics

```python
@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    response.headers["X-Process-Time"] = str(duration)
    return response
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.get("/data")
async def get_data():
    logger.info("Fetching data")
    # ... fetch data
    logger.info("Data fetched successfully")
```

---

## 🚨 Common Anti-Patterns

### ❌ Blocking the Event Loop

```python
# DON'T DO THIS
async def bad():
    time.sleep(1)  # Blocks event loop!
    requests.get(url)  # Blocks event loop!
```

### ❌ Sequential Async Operations

```python
# DON'T DO THIS
async def bad():
    user = await fetch_user()
    orders = await fetch_orders()  # Waits for user first
```

### ❌ Async for CPU-Bound

```python
# DON'T DO THIS
async def bad():
    return calculate_fibonacci(50)  # CPU-bound in async!
```

### ❌ Not Using Connection Pools

```python
# DON'T DO THIS
async def bad():
    conn = await asyncpg.connect(...)  # New connection each time!
    result = await conn.fetchrow(...)
    await conn.close()
```

---

## ✅ Best Practices Summary

1. **Use async for I/O, def for CPU**
2. **Always use connection pooling**
3. **Run independent operations concurrently** (`asyncio.gather`)
4. **Set timeouts on external calls**
5. **Use semaphores for rate limiting**
6. **Never block the event loop**
7. **Handle errors gracefully**
8. **Monitor performance** (process time, errors)
9. **Use proper logging**
10. **Test under load** before production

---

## 📚 Quick Reference

### Async Operations

| Operation | Sync | Async |
|-----------|------|-------|
| **Sleep** | `time.sleep(1)` | `await asyncio.sleep(1)` |
| **HTTP** | `requests.get()` | `await httpx.AsyncClient().get()` |
| **PostgreSQL** | `psycopg2` | `asyncpg` |
| **MySQL** | `pymysql` | `aiomysql` |
| **MongoDB** | `pymongo` | `motor` |
| **Redis** | `redis-py` | `aioredis` |
| **Files** | `open()` | `async with aiofiles.open()` |

### Performance Multipliers

| Pattern | Speedup | Use Case |
|---------|---------|----------|
| `asyncio.gather()` | 2-10x | Parallel I/O operations |
| Connection pooling | 10-100x | Database queries |
| Caching | 100-1000x | Repeated data access |
| Async HTTP client | 5-20x | External API calls |
| Uvicorn workers | N×CPU | High request volume |

---

## 🎓 Learn More

- **Tutorial**: `10_SCALABLE_APIS_TUTORIAL.md`
- **Examples**: `10_async_basics.py`, `10_async_db_operations.py`
- **Tests**: `test_scalable_apis.py`
- **Docs**: http://localhost:8000/docs
