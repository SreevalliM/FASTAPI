# FastAPI Middleware Cheatsheet

Quick reference for common middleware patterns and configurations.

## 📋 Basic Syntax

### Define Middleware
```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def my_middleware(request: Request, call_next):
    # Before endpoint
    response = await call_next(request)
    # After endpoint
    return response
```

### Using Middleware Classes
```python
app.add_middleware(
    SomeMiddleware,
    parameter1="value1",
    parameter2="value2"
)
```

## 🔧 Common Patterns

### Request Logging
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

### Request Timing
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

### Request ID Tracking
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

### Error Handling
```python
from fastapi.responses import JSONResponse

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

### Performance Monitoring
```python
@app.middleware("http")
async def monitor_performance(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    if process_time > 1.0:
        logger.warning(f"SLOW: {request.url.path} - {process_time:.2f}s")
    
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
            timeout=10.0
        )
        return response
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=504,
            content={"error": "Request timeout"}
        )
```

## 🌍 CORS Configuration

### Development (Allow All)
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False with "*"
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Production (Specific Origins)
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://myapp.com",
        "https://www.myapp.com",
        "http://localhost:3000",  # Dev only
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["X-Total-Count", "X-Request-ID"],
    max_age=600,  # Cache preflight for 10 minutes
)
```

### Environment-Based CORS
```python
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    origins = ["https://myapp.com"]
elif ENVIRONMENT == "staging":
    origins = ["https://staging.myapp.com", "http://localhost:3000"]
else:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=(ENVIRONMENT != "development"),
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🛡️ Built-in Middleware

### GZip Compression
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000  # Compress responses > 1000 bytes
)
```

### Trusted Host
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com", "localhost"]
)
```

### HTTPS Redirect
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
```

## 📊 Request State

### Store Data
```python
@app.middleware("http")
async def store_data(request: Request, call_next):
    request.state.user_id = "12345"
    request.state.start_time = time.time()
    response = await call_next(request)
    return response
```

### Access in Endpoint
```python
@app.get("/profile")
async def get_profile(request: Request):
    user_id = request.state.user_id
    return {"user_id": user_id}
```

### Access in Another Middleware
```python
@app.middleware("http")
async def use_data(request: Request, call_next):
    user_id = getattr(request.state, 'user_id', None)
    if user_id:
        logger.info(f"User: {user_id}")
    response = await call_next(request)
    return response
```

## 🎯 Request Properties

### Access Request Data
```python
@app.middleware("http")
async def inspect_request(request: Request, call_next):
    # URL info
    path = request.url.path
    query_params = request.query_params
    full_url = str(request.url)
    
    # HTTP method
    method = request.method
    
    # Headers
    content_type = request.headers.get("content-type")
    auth = request.headers.get("authorization")
    user_agent = request.headers.get("user-agent")
    
    # Client info
    client_host = request.client.host
    client_port = request.client.port
    
    # Path params (if available)
    path_params = request.path_params
    
    response = await call_next(request)
    return response
```

### Read Request Body
```python
@app.middleware("http")
async def read_body(request: Request, call_next):
    # Read body (can only be read once!)
    body = await request.body()
    
    # Store for later use
    request.state.body = body
    
    # If you need to read it again, recreate request
    async def receive():
        return {"type": "http.request", "body": body}
    
    request._receive = receive
    
    response = await call_next(request)
    return response
```

## 📝 Response Modification

### Add Headers
```python
@app.middleware("http")
async def add_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Custom-Header"] = "value"
    response.headers["X-Server"] = "FastAPI"
    return response
```

### Custom Response
```python
@app.middleware("http")
async def custom_response(request: Request, call_next):
    if request.url.path == "/blocked":
        return JSONResponse(
            status_code=403,
            content={"error": "Access denied"}
        )
    
    response = await call_next(request)
    return response
```

## 🔄 Middleware Order

```python
# Correct order (outer to inner)

# 1. CORS (outermost - handles preflight)
app.add_middleware(CORSMiddleware, ...)

# 2. Request ID (before logging)
@app.middleware("http")
async def add_request_id(...): ...

# 3. Logging (uses request ID)
@app.middleware("http")
async def logging(...): ...

# 4. Timing (measures everything below)
@app.middleware("http")
async def timing(...): ...

# 5. Authentication (after logging)
@app.middleware("http")
async def auth(...): ...

# Endpoints...
```

**Execution flow:**
```
Request
  → CORS
    → Request ID
      → Logging
        → Timing
          → Authentication
            → Endpoint
          ← Authentication
        ← Timing
      ← Logging
    ← Request ID
  ← CORS
Response
```

## 🚦 Conditional Middleware

### Path-Based
```python
@app.middleware("http")
async def api_only(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        # Only apply to /api/* endpoints
        logger.info("API request")
    
    response = await call_next(request)
    return response
```

### Method-Based
```python
@app.middleware("http")
async def post_only(request: Request, call_next):
    if request.method == "POST":
        # Only for POST requests
        logger.info("POST request")
    
    response = await call_next(request)
    return response
```

### Header-Based
```python
@app.middleware("http")
async def authenticated_only(request: Request, call_next):
    auth_header = request.headers.get("authorization")
    
    if auth_header:
        # Process authenticated requests
        pass
    
    response = await call_next(request)
    return response
```

## 📈 Rate Limiting

### Simple Rate Limiter
```python
from collections import defaultdict
import time

rate_limit_data = defaultdict(list)

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    # Get recent requests
    request_times = rate_limit_data[client_ip]
    request_times = [t for t in request_times if current_time - t < 60]
    
    # Check limit (100 per minute)
    if len(request_times) >= 100:
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )
    
    # Add current request
    request_times.append(current_time)
    rate_limit_data[client_ip] = request_times
    
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(100 - len(request_times))
    
    return response
```

## 🔐 Authentication Example

### JWT Middleware
```python
@app.middleware("http")
async def authenticate(request: Request, call_next):
    # Skip auth for public paths
    public_paths = ["/", "/login", "/docs", "/openapi.json"]
    if request.url.path in public_paths:
        return await call_next(request)
    
    # Check authorization header
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"error": "Missing authorization"}
        )
    
    # Extract token
    token = auth_header.split(" ")[1]
    
    # Validate token (pseudo-code)
    # user = validate_jwt_token(token)
    # if not user:
    #     return JSONResponse(status_code=401, content={"error": "Invalid token"})
    
    # Store user info
    # request.state.user = user
    
    response = await call_next(request)
    return response
```

## 📊 Statistics Collection

### Track Metrics
```python
from collections import defaultdict
import statistics

request_stats = defaultdict(list)

@app.middleware("http")
async def collect_stats(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Collect by endpoint
    endpoint = request.url.path
    request_stats[endpoint].append(process_time)
    
    # Add statistics headers
    times = request_stats[endpoint]
    if len(times) > 0:
        response.headers["X-Avg-Time"] = f"{statistics.mean(times):.4f}"
        response.headers["X-Request-Count"] = str(len(times))
    
    return response
```

### View Statistics Endpoint
```python
@app.get("/stats")
async def get_stats():
    stats = {}
    for endpoint, times in request_stats.items():
        if len(times) > 0:
            stats[endpoint] = {
                "count": len(times),
                "avg": f"{statistics.mean(times):.4f}s",
                "min": f"{min(times):.4f}s",
                "max": f"{max(times):.4f}s",
            }
    return stats
```

## ⚠️ Common Mistakes

### ❌ Wrong: Reading Body Multiple Times
```python
body = await request.body()  # First read
body = await request.body()  # Error!
```

### ✅ Correct: Store Body
```python
body = await request.body()
request.state.body = body  # Store for later
```

### ❌ Wrong: Blocking Call
```python
time.sleep(1)  # Blocks event loop!
```

### ✅ Correct: Async Sleep
```python
await asyncio.sleep(1)  # Non-blocking
```

### ❌ Wrong: CORS with Credentials
```python
allow_origins=["*"]
allow_credentials=True  # Error!
```

### ✅ Correct: Specific Origins
```python
allow_origins=["http://localhost:3000"]
allow_credentials=True
```

### ❌ Wrong: Forgot call_next
```python
@app.middleware("http")
async def bad_middleware(request, call_next):
    print("Oops, forgot to call call_next!")
    return Response(content="Error")
```

### ✅ Correct: Always Call call_next
```python
@app.middleware("http")
async def good_middleware(request, call_next):
    response = await call_next(request)
    return response
```

## 🧪 Testing Middleware

### Unit Test
```python
from fastapi.testclient import TestClient

def test_request_timing():
    client = TestClient(app)
    response = client.get("/")
    
    assert "X-Process-Time" in response.headers
    assert response.status_code == 200
```

### Test with curl
```bash
# Check headers
curl -i http://localhost:8000/

# Check timing
curl -i http://localhost:8000/ | grep X-Process-Time

# Test CORS
curl -X POST http://localhost:8000/data \
  -H "Origin: http://localhost:3000" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}' \
  -v
```

## 📚 Quick Reference

| Task | Code |
|------|------|
| Define middleware | `@app.middleware("http")` |
| Call next handler | `await call_next(request)` |
| Add header | `response.headers["X-Key"] = "value"` |
| Store data | `request.state.key = value` |
| Get request path | `request.url.path` |
| Get client IP | `request.client.host` |
| Get header | `request.headers.get("key")` |
| Return JSON error | `JSONResponse(status_code=400, content={})` |
| Current time | `time.time()` |
| Generate UUID | `str(uuid.uuid4())` |
| Async sleep | `await asyncio.sleep(1)` |

---

**💡 Pro Tips:**
- Always use `await` with `call_next(request)`
- Order matters - think about the execution flow
- Use `request.state` to share data between middleware
- Keep middleware focused and simple
- Handle errors gracefully
- Test CORS with actual frontend code
- Use timing headers for debugging

**🔗 See Also:**
- `07_MIDDLEWARE_TUTORIAL.md` - Detailed tutorial
- `README.md` - Module overview
- Official docs: https://fastapi.tiangolo.com/tutorial/middleware/
