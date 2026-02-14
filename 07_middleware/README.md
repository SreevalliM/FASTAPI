# 🔄 FastAPI Middleware

Comprehensive guide and examples for FastAPI middleware including logging, request timing, and CORS configuration.

## 📋 Overview

**Middleware** is code that runs before and after every request. It's perfect for cross-cutting concerns like:
- 📝 **Logging** - Track all requests and responses
- ⏱️ **Timing** - Measure request processing time
- 🌍 **CORS** - Enable cross-origin requests
- 🔐 **Authentication** - Verify user identity
- 🚦 **Rate Limiting** - Control request frequency
- 📊 **Monitoring** - Collect metrics and analytics

## 🗂️ Module Contents

### Example Files

| File | Port | Description |
|------|------|-------------|
| `07_middleware_basic.py` | 8000 | Basic middleware concepts and patterns |
| `07_logging_middleware.py` | 8001 | Advanced logging with request IDs |
| `07_timing_middleware.py` | 8002 | Request timing and performance tracking |
| `07_cors_middleware.py` | 8003 | CORS configuration and testing |

### Documentation

| File | Description |
|------|-------------|
| `07_MIDDLEWARE_TUTORIAL.md` | Complete middleware tutorial |
| `MIDDLEWARE_CHEATSHEET.md` | Quick reference guide |
| `README.md` | This file |

### Testing & Tools

| File | Description |
|------|-------------|
| `test_middleware.py` | Pytest test suite |
| `manual_test.py` | Interactive testing script |
| `quickstart.sh` | Quick setup and run script |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Using the quickstart script
chmod +x quickstart.sh
./quickstart.sh

# Or manually
pip install fastapi uvicorn pytest httpx
```

### 2. Run Basic Example

```bash
# Start the basic middleware server
python 07_middleware_basic.py

# Visit http://localhost:8000/docs
```

### 3. Test Different Examples

```bash
# Basic middleware (port 8000)
python 07_middleware_basic.py

# Advanced logging (port 8001)
python 07_logging_middleware.py

# Request timing (port 8002)
python 07_timing_middleware.py

# CORS examples (port 8003)
python 07_cors_middleware.py
```

## 📚 Key Concepts

### What is Middleware?

Middleware processes requests **before** they reach your endpoints and responses **before** they're sent to clients:

```
Request → Middleware 1 → Middleware 2 → Endpoint → Middleware 2 → Middleware 1 → Response
```

### Basic Middleware Structure

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def my_middleware(request: Request, call_next):
    # Code before endpoint
    print(f"Before: {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Code after endpoint
    print(f"After: {response.status_code}")
    
    return response
```

## 🔍 Examples

### 1. Request Logging

```python
import logging

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response
```

**Test it:**
```bash
python 07_logging_middleware.py
curl http://localhost:8001/
```

### 2. Request Timing

```python
import time

@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response
```

**Test it:**
```bash
python 07_timing_middleware.py
curl -i http://localhost:8002/fast
# Check X-Process-Time header
```

### 3. CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Test it:**
```bash
python 07_cors_middleware.py
# Visit http://localhost:8003/preflight/test-page
```

## 🧪 Testing

### Run All Tests

```bash
pytest test_middleware.py -v
```

### Run Specific Test

```bash
pytest test_middleware.py::test_request_timing -v
```

### Manual Testing

```bash
python manual_test.py
```

## 🎯 Common Use Cases

### 1. Request ID Tracking

Every request gets a unique ID for tracing:

```python
import uuid

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

### 2. Performance Monitoring

Track slow requests:

```python
@app.middleware("http")
async def monitor_performance(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    if process_time > 1.0:
        logger.warning(f"SLOW REQUEST: {request.url.path} took {process_time:.2f}s")
    
    return response
```

### 3. Error Handling

Catch and log all errors:

```python
@app.middleware("http")
async def error_handler(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
```

## 📊 Middleware Order

**Order matters!** Middleware executes in the order defined:

```python
# 1. CORS (outermost)
app.add_middleware(CORSMiddleware, ...)

# 2. Request ID
@app.middleware("http")
async def add_request_id(...): ...

# 3. Logging (uses request ID)
@app.middleware("http")
async def logging(...): ...

# 4. Timing
@app.middleware("http")
async def timing(...): ...
```

**Execution flow:**
```
Request
  → CORS
    → Request ID
      → Logging
        → Timing
          → Endpoint
        ← Timing
      ← Logging
    ← Request ID
  ← CORS
Response
```

## 🛡️ Built-in Middleware

FastAPI provides several built-in middleware options:

### CORSMiddleware
```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

### GZipMiddleware
```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### TrustedHostMiddleware
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["example.com"])
```

### HTTPSRedirectMiddleware
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
app.add_middleware(HTTPSRedirectMiddleware)
```

## 🔧 Advanced Patterns

### Conditional Middleware

```python
@app.middleware("http")
async def conditional(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        # Only apply to /api/* endpoints
        pass
    response = await call_next(request)
    return response
```

### Sharing Data Between Middleware

```python
@app.middleware("http")
async def middleware_one(request: Request, call_next):
    request.state.user_id = "12345"  # Store data
    response = await call_next(request)
    return response

@app.middleware("http")
async def middleware_two(request: Request, call_next):
    user_id = request.state.user_id  # Access data
    response = await call_next(request)
    return response
```

### Timeout Enforcement

```python
import asyncio

@app.middleware("http")
async def enforce_timeout(request: Request, call_next):
    try:
        response = await asyncio.wait_for(call_next(request), timeout=10.0)
        return response
    except asyncio.TimeoutError:
        return JSONResponse(status_code=504, content={"error": "Timeout"})
```

## ⚠️ Best Practices

### ✅ DO

- Keep middleware focused (single responsibility)
- Use async/await properly
- Handle errors gracefully
- Store shared data in `request.state`
- Use specific CORS origins in production
- Log important events
- Add timing headers for debugging

### ❌ DON'T

- Use blocking operations (e.g., `time.sleep()`)
- Read request body multiple times
- Forget to call `call_next(request)`
- Use `allow_origins=["*"]` with `allow_credentials=True`
- Ignore middleware execution order
- Swallow exceptions silently
- Do too much in one middleware

## 🐛 Common Pitfalls

### Pitfall 1: Wrong Order
```python
# ❌ Wrong: Logging before request ID
@app.middleware("http")
async def logging(request, call_next):
    print(request.state.request_id)  # Doesn't exist yet!
    ...

@app.middleware("http")
async def add_request_id(request, call_next):
    request.state.request_id = "123"
    ...
```

### Pitfall 2: Blocking Calls
```python
# ❌ Wrong: Blocks event loop
@app.middleware("http")
async def bad_middleware(request, call_next):
    time.sleep(1)  # Blocks entire server!
    ...

# ✅ Correct: Non-blocking
@app.middleware("http")
async def good_middleware(request, call_next):
    await asyncio.sleep(1)  # Non-blocking
    ...
```

### Pitfall 3: CORS Configuration
```python
# ❌ Wrong: Can't use * with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True  # Error!
)

# ✅ Correct: Specify origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True
)
```

## 📖 Learning Path

1. **Start Here**: Read `07_MIDDLEWARE_TUTORIAL.md`
2. **Basic Concepts**: Run `07_middleware_basic.py`
3. **Logging**: Explore `07_logging_middleware.py`
4. **Timing**: Study `07_timing_middleware.py`
5. **CORS**: Understand `07_cors_middleware.py`
6. **Reference**: Use `MIDDLEWARE_CHEATSHEET.md`
7. **Practice**: Write your own middleware

## 🔗 Related Topics

- **Authentication**: Module 05 - User authentication
- **Background Tasks**: Module 06 - Async task processing
- **Database**: Module 04 - Database integration
- **Dependency Injection**: Module 03 - DI patterns

## 📚 Additional Resources

- [FastAPI Middleware Docs](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Starlette Middleware](https://www.starlette.io/middleware/)
- [CORS Explained](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)

## 💡 Tips

1. **Check response headers**: Use `curl -i` or browser DevTools
2. **View logs**: Watch console output while testing
3. **Test CORS**: Use the built-in test page at `/preflight/test-page`
4. **Measure timing**: Check `X-Process-Time` headers
5. **Debug order**: Add print statements to see execution flow

## 🎓 Exercises

Try these to master middleware:

1. Create middleware that counts total requests
2. Implement a simple rate limiter
3. Add custom headers to all responses
4. Log request/response bodies (carefully!)
5. Create environment-specific CORS config
6. Build a request timeout enforcer
7. Track average response times per endpoint

## 🆘 Troubleshooting

### Middleware Not Running?
- Check if it's defined before endpoints
- Verify `await call_next(request)` is called
- Look for exceptions being swallowed

### CORS Not Working?
- Check browser console for CORS errors
- Verify origin is in `allow_origins`
- Test with curl to see actual headers
- Remember: `localhost` ≠ `127.0.0.1`

### Slow Performance?
- Check for blocking operations
- Look for excessive logging
- Verify database queries are async
- Use timing middleware to find bottlenecks

## ✨ Next Steps

After mastering middleware, explore:
- **WebSockets** - Real-time communication
- **GraphQL** - Alternative API design
- **Microservices** - Service architecture
- **Monitoring** - Production observability

---

**🎉 Happy Learning!**

For questions or issues, refer to the tutorial or check the FastAPI documentation.
