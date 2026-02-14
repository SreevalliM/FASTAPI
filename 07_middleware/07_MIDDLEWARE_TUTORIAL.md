# FastAPI Middleware Tutorial

## 📚 Table of Contents
1. [What is Middleware?](#what-is-middleware)
2. [How Middleware Works](#how-middleware-works)
3. [Creating Custom Middleware](#creating-custom-middleware)
4. [Built-in Middleware](#built-in-middleware)
5. [Logging Middleware](#logging-middleware)
6. [Request Timing](#request-timing)
7. [CORS Configuration](#cors-configuration)
8. [Advanced Patterns](#advanced-patterns)
9. [Best Practices](#best-practices)
10. [Common Pitfalls](#common-pitfalls)

---

## What is Middleware?

**Middleware** is a function that processes requests **before** they reach your endpoint handlers and processes responses **before** they're sent back to the client.

### Key Concepts

```
Client Request → Middleware 1 → Middleware 2 → Endpoint → Middleware 2 → Middleware 1 → Client Response
```

- **Request Phase**: Middleware runs top-to-bottom
- **Response Phase**: Middleware runs bottom-to-top (like a stack)
- **Order Matters**: Middleware is executed in the order it's defined

### Use Cases

Middleware is perfect for:
- ✅ Logging and monitoring
- ✅ Request timing and performance tracking
- ✅ Authentication and authorization
- ✅ CORS (Cross-Origin Resource Sharing)
- ✅ Rate limiting
- ✅ Request/Response modification
- ✅ Error handling
- ✅ Compression

---

## How Middleware Works

### Basic Structure

```python
from fastapi import FastAPI, Request
from typing import Callable

app = FastAPI()

@app.middleware("http")
async def my_middleware(request: Request, call_next: Callable):
    # Code here runs BEFORE the endpoint
    print("Before endpoint")
    
    # Call the next middleware or endpoint
    response = await call_next(request)
    
    # Code here runs AFTER the endpoint
    print("After endpoint")
    
    return response
```

### The `call_next` Function

- **`call_next(request)`**: Calls the next middleware or endpoint
- Returns a `Response` object
- Must be awaited (it's an async function)

### Request and Response Flow

```python
@app.middleware("http")
async def middleware_example(request: Request, call_next: Callable):
    # 1. Access request properties
    print(f"Method: {request.method}")
    print(f"URL: {request.url}")
    print(f"Headers: {request.headers}")
    
    # 2. Modify request (store data in request.state)
    request.state.custom_data = "some value"
    
    # 3. Process the request
    response = await call_next(request)
    
    # 4. Modify response
    response.headers["X-Custom-Header"] = "value"
    
    # 5. Return response
    return response
```

---

## Creating Custom Middleware

### Method 1: Using @app.middleware("http")

**Pros**: Simple, Pythonic, direct access to Request/Response
**Cons**: Limited customization

```python
from fastapi import FastAPI, Request
import time

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Method 2: Using Starlette Middleware Classes

**Pros**: More control, reusable, configurable
**Cons**: More boilerplate

```python
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request

class CustomMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, custom_param: str):
        super().__init__(app)
        self.custom_param = custom_param
    
    async def dispatch(self, request: Request, call_next):
        # Middleware logic
        print(f"Param: {self.custom_param}")
        response = await call_next(request)
        return response

app = FastAPI()
app.add_middleware(CustomMiddleware, custom_param="value")
```

### Method 3: Pure ASGI Middleware

**Pros**: Maximum control, highest performance
**Cons**: Most complex, low-level

```python
class ASGIMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Middleware logic
            pass
        await self.app(scope, receive, send)

app = FastAPI()
app.add_middleware(ASGIMiddleware)
```

---

## Built-in Middleware

FastAPI/Starlette provides several built-in middleware options:

### 1. CORSMiddleware

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

### 2. TrustedHostMiddleware

Protects against Host header attacks:

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)
```

### 3. GZipMiddleware

Compresses responses:

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 4. HTTPSRedirectMiddleware

Redirects HTTP to HTTPS:

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
```

---

## Logging Middleware

### Basic Request Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response
```

### Advanced Logging with Request IDs

```python
import uuid

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    logger.info(f"[{request_id}] Status: {response.status_code}")
    
    return response
```

### Logging Request/Response Bodies

```python
@app.middleware("http")
async def log_request_body(request: Request, call_next):
    # Read request body
    body = await request.body()
    logger.info(f"Request body: {body.decode()}")
    
    # Important: Create new request with body
    # (because body can only be read once)
    async def receive():
        return {"type": "http.request", "body": body}
    
    request._receive = receive
    
    response = await call_next(request)
    return response
```

### Structured Logging

```python
import json

@app.middleware("http")
async def structured_logging(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    log_data = {
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "client_ip": request.client.host,
        "user_agent": request.headers.get("user-agent"),
    }
    
    response = await call_next(request)
    
    log_data.update({
        "status_code": response.status_code,
        "process_time": time.time() - start_time,
    })
    
    logger.info(json.dumps(log_data))
    
    return response
```

---

## Request Timing

### Basic Timing

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

### Detailed Timing with Breakdown

```python
@app.middleware("http")
async def detailed_timing(request: Request, call_next):
    timings = {}
    
    # Store start time
    start_time = time.time()
    request.state.timings = timings
    request.state.start_time = start_time
    
    # Process request
    response = await call_next(request)
    
    # Calculate total time
    total_time = time.time() - start_time
    response.headers["X-Total-Time"] = f"{total_time:.4f}"
    
    return response
```

### Using Timing in Endpoints

```python
@app.get("/example")
async def example(request: Request):
    # Access timing info from middleware
    start_time = request.state.start_time
    
    # Do some work
    await asyncio.sleep(0.5)
    
    # Record timing
    request.state.timings["work"] = time.time() - start_time
    
    return {"message": "done"}
```

### Performance Monitoring

```python
@app.middleware("http")
async def performance_monitoring(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Alert on slow requests
    if process_time > 1.0:
        logger.warning(
            f"SLOW REQUEST: {request.method} {request.url.path} "
            f"took {process_time:.2f}s"
        )
    
    return response
```

### Timeout Enforcement

```python
import asyncio

@app.middleware("http")
async def enforce_timeout(request: Request, call_next):
    try:
        response = await asyncio.wait_for(
            call_next(request),
            timeout=10.0  # 10 second timeout
        )
        return response
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=504,
            content={"error": "Request timeout"}
        )
```

---

## CORS Configuration

### What is CORS?

**CORS (Cross-Origin Resource Sharing)** is a security feature that restricts web pages from making requests to a different domain than the one serving the page.

### When Do You Need CORS?

You need CORS when:
- Your frontend (e.g., React at `localhost:3000`) calls your API (at `localhost:8000`)
- Your frontend is at `app.example.com` and API is at `api.example.com`
- Any time the **origin** (protocol + domain + port) differs

### Basic CORS Setup (Development)

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# WARNING: Only for development!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Production CORS Setup

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://myapp.com",
        "https://www.myapp.com",
        "http://localhost:3000",  # Dev only
    ],
    allow_credentials=True,  # Allow cookies
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["X-Total-Count"],  # Headers accessible to JS
    max_age=600,  # Cache preflight for 10 minutes
)
```

### CORS Parameters Explained

| Parameter | Description | Example |
|-----------|-------------|---------|
| `allow_origins` | Which origins can access the API | `["https://myapp.com"]` |
| `allow_credentials` | Allow cookies and auth headers | `True` |
| `allow_methods` | Which HTTP methods are allowed | `["GET", "POST"]` |
| `allow_headers` | Which request headers are allowed | `["Authorization"]` |
| `expose_headers` | Which response headers JS can access | `["X-Total-Count"]` |
| `max_age` | How long to cache preflight requests | `600` (seconds) |

### Understanding Preflight Requests

Some requests trigger a **preflight** OPTIONS request:

**Simple requests (no preflight):**
- GET, HEAD, POST
- Simple headers (Content-Type: text/plain, etc.)

**Complex requests (with preflight):**
- PUT, DELETE, PATCH
- POST with Content-Type: application/json
- Custom headers (Authorization, etc.)

```python
# Browser automatically sends:
OPTIONS /api/data HTTP/1.1
Origin: http://localhost:3000
Access-Control-Request-Method: POST
Access-Control-Request-Headers: content-type

# Server responds:
HTTP/1.1 200 OK
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: POST
Access-Control-Allow-Headers: content-type
```

### Environment-Based CORS

```python
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    allowed_origins = ["https://myapp.com"]
elif ENVIRONMENT == "staging":
    allowed_origins = ["https://staging.myapp.com", "http://localhost:3000"]
else:
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=(ENVIRONMENT != "development"),
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Testing CORS

**Using curl:**
```bash
# Simulate CORS request
curl -X POST http://localhost:8000/api/data \
  -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}' \
  -v
```

**Using JavaScript:**
```javascript
fetch('http://localhost:8000/api/data', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ test: 'data' })
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## Advanced Patterns

### Middleware Ordering

**Order matters!** Middleware executes in the order defined:

```python
# 1. Add CORS first (outermost)
app.add_middleware(CORSMiddleware, ...)

# 2. Then request ID
@app.middleware("http")
async def add_request_id(request, call_next):
    ...

# 3. Then logging (uses request ID)
@app.middleware("http")
async def log_requests(request, call_next):
    ...

# 4. Then timing
@app.middleware("http")
async def add_timing(request, call_next):
    ...
```

### Conditional Middleware

```python
@app.middleware("http")
async def conditional_middleware(request: Request, call_next):
    # Only apply to certain paths
    if request.url.path.startswith("/api/"):
        # Apply middleware logic
        print("API request")
    
    response = await call_next(request)
    return response
```

### Storing Data in Request State

```python
@app.middleware("http")
async def add_user_info(request: Request, call_next):
    # Store data for access in endpoints
    request.state.user_id = "12345"
    request.state.user_name = "John"
    
    response = await call_next(request)
    return response

@app.get("/profile")
async def get_profile(request: Request):
    # Access middleware data
    user_id = request.state.user_id
    return {"user_id": user_id}
```

### Error Handling in Middleware

```python
@app.middleware("http")
async def error_handling(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"error": "Bad request", "detail": str(e)}
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )
```

### Authentication Middleware

```python
from fastapi import HTTPException

@app.middleware("http")
async def authenticate(request: Request, call_next):
    # Skip auth for public endpoints
    if request.url.path in ["/", "/login", "/docs"]:
        return await call_next(request)
    
    # Check authorization header
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"error": "Missing or invalid authorization"}
        )
    
    # Extract and validate token
    token = auth_header.split(" ")[1]
    # ... validate token ...
    
    # Store user info
    request.state.user_id = "extracted_from_token"
    
    response = await call_next(request)
    return response
```

### Rate Limiting

```python
from collections import defaultdict
import time

# Simple in-memory rate limiter
rate_limit_data = defaultdict(list)

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Get request times for this IP
    request_times = rate_limit_data[client_ip]
    
    # Remove old requests (older than 1 minute)
    request_times = [t for t in request_times if current_time - t < 60]
    
    # Check limit (e.g., 100 requests per minute)
    if len(request_times) >= 100:
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )
    
    # Add current request
    request_times.append(current_time)
    rate_limit_data[client_ip] = request_times
    
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = str(100 - len(request_times))
    
    return response
```

---

## Best Practices

### 1. Keep Middleware Focused

✅ **Good**: Single responsibility
```python
@app.middleware("http")
async def add_request_id(request, call_next):
    request.state.request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response
```

❌ **Bad**: Doing too much
```python
@app.middleware("http")
async def do_everything(request, call_next):
    # Don't: logging, timing, auth, rate limiting all in one
    ...
```

### 2. Order Matters

```python
# Correct order
app.add_middleware(CORSMiddleware, ...)  # First
@app.middleware("http")
async def request_id(...): ...           # Second
@app.middleware("http")
async def logging(...): ...              # Third (uses request ID)
```

### 3. Use Request State for Sharing Data

```python
# Store in middleware
request.state.request_id = "123"
request.state.user = user_obj

# Access in endpoint
@app.get("/")
async def endpoint(request: Request):
    request_id = request.state.request_id
```

### 4. Handle Errors Gracefully

```python
@app.middleware("http")
async def safe_middleware(request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Internal error"})
```

### 5. Be Careful with Request Body

```python
# Request body can only be read once!
body = await request.body()  # First read

# If you need it again, store it
request.state.body = body

# Or recreate the request
```

### 6. Use Async Properly

```python
# ✅ Good: Using await
@app.middleware("http")
async def good_middleware(request, call_next):
    await some_async_function()
    response = await call_next(request)
    return response

# ❌ Bad: Blocking call
@app.middleware("http")
async def bad_middleware(request, call_next):
    time.sleep(1)  # Blocks event loop!
    response = await call_next(request)
    return response

# ✅ Good: Use asyncio.sleep for delays
@app.middleware("http")
async def good_middleware(request, call_next):
    await asyncio.sleep(1)  # Non-blocking
    response = await call_next(request)
    return response
```

### 7. CORS: Production vs Development

```python
# Development
if DEBUG:
    app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Production
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://myapp.com"],
        allow_credentials=True
    )
```

---

## Common Pitfalls

### ❌ Pitfall 1: Reading Request Body Multiple Times

```python
# Wrong:
@app.middleware("http")
async def bad_middleware(request, call_next):
    body = await request.body()  # First read
    # ... later ...
    body = await request.body()  # Error: can't read again!
```

**Solution:**
```python
# Correct:
@app.middleware("http")
async def good_middleware(request, call_next):
    body = await request.body()
    request.state.body = body  # Store for later use
```

### ❌ Pitfall 2: Wrong Middleware Order

```python
# Wrong: Logging before request ID
@app.middleware("http")
async def logging(...): 
    print(request.state.request_id)  # Error: doesn't exist yet!

@app.middleware("http")
async def add_request_id(...):
    request.state.request_id = "123"
```

**Solution:** Define middleware in correct order (request ID first).

### ❌ Pitfall 3: Forgetting to Call call_next

```python
# Wrong:
@app.middleware("http")
async def bad_middleware(request, call_next):
    print("Before endpoint")
    # Forgot to call call_next!
    return Response(content="Oops")
```

**Solution:** Always call `await call_next(request)`.

### ❌ Pitfall 4: Blocking Operations

```python
# Wrong:
@app.middleware("http")
async def bad_middleware(request, call_next):
    time.sleep(1)  # Blocks entire server!
    response = await call_next(request)
    return response
```

**Solution:** Use `await asyncio.sleep(1)`.

### ❌ Pitfall 5: CORS with Credentials

```python
# Wrong:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True  # Error: Can't use * with credentials!
)
```

**Solution:** Specify exact origins when using credentials.

### ❌ Pitfall 6: Not Handling Exceptions

```python
# Wrong:
@app.middleware("http")
async def bad_middleware(request, call_next):
    response = await call_next(request)  # What if this raises an error?
    return response
```

**Solution:** Wrap in try/except.

---

## Summary

### Key Takeaways

1. **Middleware** processes requests before endpoints and responses after
2. **Order matters**: Define middleware in correct sequence
3. **Use `call_next(request)`**: To pass control to next middleware/endpoint
4. **Store data in `request.state`**: For sharing between middleware and endpoints
5. **CORS is essential**: For frontend-backend communication
6. **Always handle errors**: Prevent middleware from breaking your app
7. **Keep it async**: Use `await`, not blocking calls

### Quick Reference

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# Built-in middleware
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# Custom middleware
@app.middleware("http")
async def timer(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.time() - start)
    return response

# Endpoint
@app.get("/")
async def root():
    return {"message": "Hello"}
```

---

## Next Steps

1. ✅ Run the example files in this module
2. ✅ Experiment with different middleware combinations
3. ✅ Test CORS with a frontend application
4. ✅ Implement authentication middleware
5. ✅ Add monitoring and logging to your API

---

**🎉 You now understand FastAPI middleware!**

For more examples, see:
- `07_middleware_basic.py` - Basic middleware concepts
- `07_logging_middleware.py` - Advanced logging patterns
- `07_timing_middleware.py` - Request timing and monitoring
- `07_cors_middleware.py` - CORS configuration examples
