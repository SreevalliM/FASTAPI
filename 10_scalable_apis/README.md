# 10. Writing Scalable APIs with FastAPI 🚀

Learn how to build high-performance, scalable APIs using async/await, proper concurrency patterns, and production-ready deployment strategies.

## 📚 What You'll Learn

- ✅ **async def vs def**: When and why to use each
- ✅ **Event Loop Basics**: Understanding the core of async programming
- ✅ **Async Database Drivers**: Non-blocking database operations
- ✅ **Concurrency Patterns**: Parallel execution, timeouts, rate limiting
- ✅ **ASGI vs WSGI**: Modern async vs traditional sync interfaces
- ✅ **Uvicorn & Gunicorn**: Production server configuration
- ✅ **When to Use Async**: Decision-making framework
- ✅ **Performance Best Practices**: Optimization techniques
- ✅ **Production Deployment**: Docker, Kubernetes, monitoring

## 📁 Module Contents

```
10_scalable_apis/
├── 10_SCALABLE_APIS_TUTORIAL.md      # Comprehensive tutorial
├── 10_async_basics.py                # Async vs sync fundamentals
├── 10_async_db_operations.py         # Database async patterns
├── 10_concurrency_patterns.py        # Advanced concurrency
├── 10_production_deployment.py       # Production configuration
├── SCALABLE_APIS_CHEATSHEET.md       # Quick reference
├── README.md                          # This file
├── test_scalable_apis.py             # Automated tests
├── manual_test.py                     # Manual testing script
├── quickstart.sh                      # Quick setup script
└── gunicorn.conf.py                   # Production server config
```

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+ required
python --version

# Activate virtual environment
source ../fastapi-env/bin/activate  # macOS/Linux
# or
../fastapi-env/Scripts/activate  # Windows
```

### Installation

```bash
# Run the quickstart script
chmod +x quickstart.sh
./quickstart.sh

# Or install dependencies manually
pip install fastapi uvicorn[standard] httpx aiosqlite psutil gunicorn
```

### Run Examples

```bash
# 1. Async Basics (Port 8000)
python 10_async_basics.py

# 2. Async DB Operations (Port 8001)
python 10_async_db_operations.py

# 3. Concurrency Patterns (Port 8002)
python 10_concurrency_patterns.py

# 4. Production Deployment (Port 8003)
python 10_production_deployment.py
```

### Access Documentation

- Async Basics: http://localhost:8000/docs
- Async DB: http://localhost:8001/docs
- Concurrency: http://localhost:8002/docs
- Production: http://localhost:8003/docs

## 📖 Learning Path

### 1. Start with the Tutorial

Read [`10_SCALABLE_APIS_TUTORIAL.md`](10_SCALABLE_APIS_TUTORIAL.md) for comprehensive explanations of all concepts.

### 2. Run the Examples

**Async Basics** (`10_async_basics.py`)
- Compare sync vs async endpoints
- See event loop in action
- Performance benchmarks
- Best practices

```bash
python 10_async_basics.py
# Try: http://localhost:8000/compare/sync-vs-async?requests=5
```

**Async DB Operations** (`10_async_db_operations.py`)
- CRUD with async database drivers
- Connection pooling
- Concurrent queries
- Transaction handling

```bash
python 10_async_db_operations.py
# Try: POST http://localhost:8001/seed-data
#      GET http://localhost:8001/dashboard/1
```

**Concurrency Patterns** (`10_concurrency_patterns.py`)
- `asyncio.gather()` for parallel execution
- Timeouts with `asyncio.wait_for()`
- Rate limiting with Semaphores
- Background task management

```bash
python 10_concurrency_patterns.py
# Try: GET http://localhost:8002/parallel/gather
#      GET http://localhost:8002/rate-limiting/semaphore
```

**Production Deployment** (`10_production_deployment.py`)
- Health checks
- Monitoring
- Graceful shutdown
- Production configuration

```bash
python 10_production_deployment.py
# Try: GET http://localhost:8003/health/detailed
#      GET http://localhost:8003/metrics
```

### 3. Study the Cheat Sheet

Refer to [`SCALABLE_APIS_CHEATSHEET.md`](SCALABLE_APIS_CHEATSHEET.md) for quick references while coding.

### 4. Run Tests

```bash
# Run all tests
pytest test_scalable_apis.py -v

# Run specific test
pytest test_scalable_apis.py::test_async_faster_than_sync -v

# Run with coverage
pytest test_scalable_apis.py --cov=. --cov-report=html
```

### 5. Manual Testing

```bash
python manual_test.py
```

## 🎯 Key Concepts

### Async def vs def

```python
# Use async def for I/O-bound operations
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await db.fetch_one("SELECT * FROM users WHERE id = $1", user_id)
    return user

# Use def for CPU-bound operations
@app.get("/calculate")
def calculate(n: int):
    return fibonacci(n)
```

### Concurrent Operations

```python
# Sequential (slow) - Total time: 1.5s
user = await fetch_user()      # 0.5s
orders = await fetch_orders()  # 1.0s

# Concurrent (fast) - Total time: 1.0s
user, orders = await asyncio.gather(
    fetch_user(),    # 0.5s
    fetch_orders()   # 1.0s
)
```

### Connection Pooling

```python
# Create pool once at startup
db_pool = await asyncpg.create_pool(
    "postgresql://...",
    min_size=10,
    max_size=20
)

# Reuse connections
async with db_pool.acquire() as conn:
    result = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
```

## 🚀 Production Deployment

### Using Uvicorn (Development)

```bash
uvicorn 10_async_basics:app --reload
```

### Using Gunicorn + Uvicorn (Production)

```bash
# Calculate workers: (2 × CPU_cores) + 1
gunicorn 10_production_deployment:app \
  --workers 9 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 30
```

### Using Configuration File

```bash
gunicorn 10_production_deployment:app -c gunicorn.conf.py
```

### Docker Deployment

```bash
# Build image
docker build -t scalable-api .

# Run container
docker run -p 8000:8000 scalable-api
```

### Docker Compose

```bash
docker-compose up -d
```

## 📊 Performance Tips

1. **Use Connection Pooling** - 10-100x faster database queries
2. **Run Concurrent Operations** - 2-10x speedup with `asyncio.gather()`
3. **Set Timeouts** - Prevent hanging requests
4. **Rate Limiting** - Protect against overload
5. **Caching** - 100-1000x speedup for repeated data
6. **Monitor Performance** - Track slow requests

## 🔍 Testing Endpoints

### Manual Testing with cURL

```bash
# Compare sync vs async
curl http://localhost:8000/compare/sync-vs-async?requests=5

# Test concurrent queries
curl http://localhost:8001/dashboard/1

# Test parallel execution
curl http://localhost:8002/parallel/gather

# Health check
curl http://localhost:8003/health/detailed
```

### Load Testing

```bash
# Install Apache Bench
# macOS: brew install httpd
# Ubuntu: sudo apt-get install apache2-utils

# Test with 1000 requests, 100 concurrent
ab -n 1000 -c 100 http://localhost:8000/async/sleep?seconds=0

# Or use wrk
wrk -t12 -c400 -d30s http://localhost:8000/
```

## 🐛 Common Issues & Solutions

### Issue: "Event loop is closed"

**Solution**: Don't call `asyncio.run()` inside FastAPI endpoints. FastAPI manages the event loop.

```python
# ❌ Don't do this
@app.get("/data")
async def get_data():
    result = asyncio.run(fetch_data())  # ERROR!

# ✅ Do this
@app.get("/data")
async def get_data():
    result = await fetch_data()  # Correct
```

### Issue: Slow async endpoints

**Solution**: Check if you're blocking the event loop

```python
# ❌ Don't do this
async def bad():
    time.sleep(1)  # Blocks!

# ✅ Do this
async def good():
    await asyncio.sleep(1)  # Non-blocking
```

### Issue: Database connection errors

**Solution**: Use connection pooling and proper error handling

```python
try:
    async with db_pool.acquire() as conn:
        result = await conn.fetchrow("SELECT ...")
except Exception as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Database error")
```

## 📈 Performance Benchmarks

Results from running examples (your results may vary):

| Endpoint | Requests | Sync Time | Async Time | Speedup |
|----------|----------|-----------|------------|---------|
| Sleep operations | 10 | 10.0s | 1.0s | 10x |
| Database queries | 5 | 0.5s | 0.1s | 5x |
| HTTP requests | 10 | 10.0s | 1.0s | 10x |
| Concurrent dashboard | 1 | 0.37s | 0.15s | 2.5x |

## 🎓 Learning Resources

### Official Documentation
- [FastAPI Async](https://fastapi.tiangolo.com/async/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
- [Uvicorn](https://www.uvicorn.org/)
- [Gunicorn](https://gunicorn.org/)

### Database Drivers
- [asyncpg](https://magicstack.github.io/asyncpg/) - PostgreSQL
- [motor](https://motor.readthedocs.io/) - MongoDB
- [aiosqlite](https://aiosqlite.omnilib.dev/) - SQLite
- [aiomysql](https://aiomysql.readthedocs.io/) - MySQL

### Advanced Topics
- [httpx](https://www.python-httpx.org/) - Async HTTP client
- [aiofiles](https://github.com/Tinche/aiofiles) - Async file operations
- [aioredis](https://aioredis.readthedocs.io/) - Async Redis

## 🎯 Exercises

### Exercise 1: Optimize Sequential Queries
Modify the code in `10_async_db_operations.py` to run queries concurrently instead of sequentially.

### Exercise 2: Add Timeout Handling
Add timeout handling to external API calls in `10_concurrency_patterns.py`.

### Exercise 3: Implement Rate Limiting
Create a rate limiter that limits requests per user to 10 requests per minute.

### Exercise 4: Add Monitoring
Implement Prometheus metrics collection for your API endpoints.

### Exercise 5: Load Testing
Use `wrk` or `Apache Bench` to load test your API and find the bottlenecks.

## 🔧 Troubleshooting

### Virtual Environment Issues

```bash
# Recreate virtual environment
deactivate
rm -rf ../fastapi-env
python -m venv ../fastapi-env
source ../fastapi-env/bin/activate
pip install -r ../requirements.txt
```

### Port Already in Use

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python 10_async_basics.py --port 8001
```

### Module Import Errors

```bash
# Ensure you're in the correct directory
cd 10_scalable_apis

# Run with module syntax
python -m 10_async_basics
```

## 🤝 Next Steps

After completing this module:
1. **Build a real application** - Apply these concepts to a real project
2. **Stress test** - Use load testing tools to find limits
3. **Monitor in production** - Set up proper logging and metrics
4. **Optimize further** - Profile your code and optimize bottlenecks
5. **Learn advanced patterns** - Circuit breakers, retries, caching strategies

## 📝 Additional Notes

### When to Scale Horizontally vs Vertically

**Vertical Scaling** (bigger machines):
- Easier to implement
- Good for CPU-bound workloads
- Limited by hardware

**Horizontal Scaling** (more machines):
- Better for async I/O workloads
- Requires load balancing
- Unlimited scaling potential

### Production Checklist

- [ ] Use connection pooling
- [ ] Set timeouts on external calls
- [ ] Implement health checks
- [ ] Add monitoring and logging
- [ ] Use proper error handling
- [ ] Configure CORS properly
- [ ] Use HTTPS
- [ ] Implement rate limiting
- [ ] Set up CI/CD
- [ ] Load test before deployment

## 🎉 Summary

You've learned how to:
- ✅ Write async vs sync endpoints correctly
- ✅ Use async database drivers efficiently
- ✅ Implement concurrency patterns
- ✅ Deploy to production with Gunicorn + Uvicorn
- ✅ Monitor and optimize performance
- ✅ Make informed decisions about when to use async

**Next Module**: Continue exploring FastAPI advanced features or build your own scalable application!

---

**Need Help?** 
- Check the tutorial: `10_SCALABLE_APIS_TUTORIAL.md`
- Check the cheat sheet: `SCALABLE_APIS_CHEATSHEET.md`
- Run the tests: `pytest test_scalable_apis.py -v`
- Review examples: `10_async_basics.py`, `10_async_db_operations.py`

Happy coding! 🚀
