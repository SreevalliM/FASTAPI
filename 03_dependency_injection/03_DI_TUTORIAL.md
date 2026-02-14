# 🎓 FastAPI Dependency Injection - Complete Tutorial

## What is Dependency Injection?

**Dependency Injection (DI)** is a design pattern where components receive their dependencies from external sources rather than creating them internally.

### Benefits:
- ✅ **Code Reusability** - Write once, use everywhere
- ✅ **Separation of Concerns** - Logic is modular and organized
- ✅ **Easy Testing** - Dependencies can be easily mocked
- ✅ **Shared Resources** - DB connections, loggers, configs
- ✅ **Security** - Centralized authentication/authorization

---

## 📖 Core Concept: `Depends()`

FastAPI's `Depends()` is used to declare dependencies that should run before your endpoint.

```python
from fastapi import Depends

def common_logic():
    return {"message": "I run first!"}

@app.get("/")
def my_endpoint(result: dict = Depends(common_logic)):
    return result
```

**Flow:**
1. Request comes in → `/`
2. FastAPI sees `Depends(common_logic)`
3. Runs `common_logic()` first
4. Passes result to `my_endpoint`
5. Returns response

---

## 🔧 Types of Dependencies

### 1. Function-Based Dependencies

```python
def verify_token(token: str = Header(...)):
    if token != "secret":
        raise HTTPException(401, "Invalid token")
    return {"user": "john"}

@app.get("/protected")
def protected_route(user: dict = Depends(verify_token)):
    return user
```

### 2. Class-Based Dependencies

```python
class Logger:
    def __call__(self, request: Request):
        print(f"Request to {request.url}")
        return {"logged": True}

logger = Logger()

@app.get("/")
def endpoint(log: dict = Depends(logger)):
    return {"status": "ok"}
```

### 3. Generator-Based Dependencies (with cleanup)

```python
def get_db():
    db = Database()  # Setup
    try:
        yield db  # Use
    finally:
        db.close()  # Cleanup (always runs)

@app.get("/users")
def get_users(db: Database = Depends(get_db)):
    return db.query_users()
```

**Generator dependencies are perfect for:**
- Database sessions
- File handles
- Network connections
- Any resource that needs cleanup

---

## 🔗 Dependency Chaining

Dependencies can depend on other dependencies:

```python
# Level 1: Authenticate user
def get_current_user(api_key: str = Header(...)):
    if api_key not in valid_keys:
        raise HTTPException(401, "Invalid key")
    return {"username": "john", "role": "user"}

# Level 2: Check if admin (depends on get_current_user)
def require_admin(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(403, "Admin required")
    return user

# Endpoint uses require_admin (which chains get_current_user)
@app.delete("/users/{id}")
def delete_user(
    id: int,
    admin: dict = Depends(require_admin)  # Automatically calls get_current_user
):
    return {"deleted": id, "by": admin["username"]}
```

**Benefits of Chaining:**
- Reusable authorization layers
- Clear security hierarchy
- DRY principle (Don't Repeat Yourself)

---

## 📚 Real-World Examples in Our API

### Example 1: Logging Dependency

```python
class LoggingDependency:
    def __call__(self, request: Request):
        logger.info(f"📥 {request.method} {request.url.path}")
        return {"timestamp": datetime.now(), "path": request.url.path}

log_request = LoggingDependency()

@app.post("/users")
def create_user(
    user: UserCreate,
    log_info: dict = Depends(log_request)  # Logs every request
):
    # Your logic here
    pass
```

**Why it's useful:**
- Automatic logging for all endpoints
- Consistent log format
- Easy to modify logging logic in one place

### Example 2: Rate Limiting Dependency

```python
class RateLimiter:
    def __init__(self, requests: int = 10, window_seconds: int = 60):
        self.max_requests = requests
        self.window = timedelta(seconds=window_seconds)
    
    def __call__(self, request: Request):
        client_ip = request.client.host
        # Check request history
        if too_many_requests(client_ip):
            raise HTTPException(429, "Rate limit exceeded")
        return {"requests_remaining": calculate_remaining()}

rate_limiter = RateLimiter(requests=10, window_seconds=60)

@app.post("/users")
def create_user(
    user: UserCreate,
    rate_limit: dict = Depends(rate_limiter)  # Max 10 requests/minute
):
    pass
```

**Why it's useful:**
- Prevents abuse
- Different limits for different endpoints
- IP-based tracking

### Example 3: Database Session Dependency

```python
def get_db():
    db = DatabaseSession()
    try:
        yield db  # This is what gets injected
    finally:
        db.close()  # Always closes, even if error occurs

@app.get("/users")
def get_users(db: DatabaseSession = Depends(get_db)):
    return db.query("SELECT * FROM users")
    # db.close() is called automatically after this function
```

**Why it's useful:**
- Guaranteed cleanup (no leaked connections)
- Connection pooling
- Transaction management

### Example 4: Security Dependencies

```python
# Authentication
def verify_api_key(api_key: str = Header(...)):
    if api_key not in valid_keys:
        raise HTTPException(401, "Invalid API key")
    return api_keys[api_key]  # Returns user info

# Authorization (chains authentication)
def verify_admin(user: dict = Depends(verify_api_key)):
    if user["role"] != "admin":
        raise HTTPException(403, "Admin access required")
    return user

# Public endpoint - no dependency
@app.get("/")
def home():
    return {"status": "ok"}

# Protected endpoint - requires API key
@app.get("/users")
def list_users(user: dict = Depends(verify_api_key)):
    return users

# Admin-only endpoint - requires admin role
@app.delete("/users/{id}")
def delete_user(id: int, admin: dict = Depends(verify_admin)):
    return {"deleted": id}
```

---

## 🧪 Testing Dependencies

One of the biggest advantages of DI is easy testing:

```python
# Original dependency
def get_real_db():
    return RealDatabase()

# Test override
def get_fake_db():
    return FakeDatabase()

# In tests
app.dependency_overrides[get_real_db] = get_fake_db

# Now all endpoints using get_real_db will get FakeDatabase instead!
```

---

## 🎯 Practice Project Walkthrough

Our User Management API demonstrates:

### 1. ✅ **Logging Dependency**
- Logs every request automatically
- Tracks IP, method, path
- See: `LoggingDependency` class

### 2. ✅ **Rate Limiting**
- Prevents abuse (10 req/min normal, 5 req/min admin)
- IP-based tracking
- See: `RateLimiter` class

### 3. ✅ **Email Validation**
- Validates email format (Pydantic `EmailStr`)
- Checks allowed domains
- See: `validate_email_domain()` function

### 4. ✅ **Authentication**
- API key validation
- User identification
- See: `verify_api_key()` function

### 5. ✅ **Authorization**
- Role-based access control (admin vs user)
- Dependency chaining
- See: `verify_admin()` function (depends on `verify_api_key`)

### 6. ✅ **Database Session**
- Simulated DB connection
- Automatic cleanup
- See: `get_db()` generator

---

## 🚀 How to Run the Project

### 1. Start the Server

```bash
cd /Users/L107127/Library/CloudStorage/OneDrive-EliLillyandCompany/Desktop/FASTAPI
python 03_dependency_injection.py
```

### 2. Open Documentation

Visit: http://localhost:8000/docs

### 3. Test the API

#### Test 1: Create User (No auth required)

```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@gmail.com",
    "age": 25,
    "password": "securepass123"
  }'
```

**Dependencies executed:**
- ✅ Logging (logs request)
- ✅ Rate limiting (checks limit)
- ✅ Database session (manages DB)
- ✅ Email validation (checks domain)

#### Test 2: List Users (Auth required)

```bash
curl -X GET "http://localhost:8000/users" \
  -H "api_key: user_key_456"
```

**Dependencies executed:**
- ✅ Logging
- ✅ Rate limiting
- ✅ Authentication (validates API key)
- ✅ Database session

#### Test 3: Delete User (Admin only)

```bash
curl -X DELETE "http://localhost:8000/users/1" \
  -H "api_key: admin_key_123"
```

**Dependencies executed:**
- ✅ Logging
- ✅ Rate limiting (strict: 5/min)
- ✅ Authentication (via `verify_api_key`)
- ✅ Authorization (checks admin role)
- ✅ Database session

#### Test 4: Trigger Rate Limit

Run this multiple times quickly:

```bash
for i in {1..12}; do
  curl -X GET "http://localhost:8000/rate-limit-status"
done
```

You'll see `429 Too Many Requests` after 10 requests.

---

## 🎓 Key Takeaways

### When to Use Dependencies:

| Use Case | Dependency Type | Example |
|----------|----------------|---------|
| Logging | Class-based | `LoggingDependency` |
| Authentication | Function-based | `verify_api_key()` |
| Authorization | Function-based (chained) | `verify_admin()` |
| DB Connection | Generator-based | `get_db()` |
| Rate Limiting | Class-based | `RateLimiter` |
| Validation | Function-based | `validate_email_domain()` |

### Best Practices:

1. **Use generators for resources that need cleanup**
   ```python
   def get_db():
       db = connect()
       try:
           yield db
       finally:
           db.close()
   ```

2. **Chain dependencies for authorization**
   ```python
   def require_admin(user = Depends(get_user)):
       check_admin(user)
   ```

3. **Create reusable class-based dependencies**
   ```python
   class RateLimiter:
       def __init__(self, limit: int):
           self.limit = limit
       def __call__(self, request: Request):
           check_limit(request)
   ```

4. **Use `Annotated` for cleaner code**
   ```python
   from typing import Annotated
   
   CurrentUser = Annotated[dict, Depends(get_current_user)]
   
   def endpoint(user: CurrentUser):  # Cleaner!
       pass
   ```

---

## 🔍 Dependency Execution Order

```python
@app.post("/users")
def create_user(
    user: UserCreate,                          # 1. Request body parsed
    log: dict = Depends(log_request),         # 2. Logging runs
    rate: dict = Depends(rate_limiter),       # 3. Rate limit checked
    api_key: dict = Depends(verify_api_key),  # 4. Authentication
    db: Database = Depends(get_db),           # 5. DB session created
):
    # 6. Your endpoint logic runs here
    pass
    # 7. DB session closed (if generator)
```

**Dependencies run in the order they're declared!**

---

## 📝 Practice Exercises

### Exercise 1: Add Request ID Dependency
Create a dependency that adds a unique request ID to every request.

```python
import uuid

def add_request_id():
    return {"request_id": str(uuid.uuid4())}

@app.get("/test")
def test(req_id: dict = Depends(add_request_id)):
    return req_id
```

### Exercise 2: Add Cache Dependency
Create a simple in-memory cache dependency.

```python
cache = {}

def get_cache():
    return cache

@app.get("/items/{id}")
def get_item(id: int, cache: dict = Depends(get_cache)):
    if id in cache:
        return cache[id]
    # Fetch from DB...
    cache[id] = result
    return result
```

### Exercise 3: Add IP Whitelist Dependency
Only allow certain IPs to access endpoints.

```python
ALLOWED_IPS = ["127.0.0.1", "192.168.1.100"]

def check_ip(request: Request):
    if request.client.host not in ALLOWED_IPS:
        raise HTTPException(403, "IP not allowed")
    return request.client.host

@app.get("/admin")
def admin_panel(ip: str = Depends(check_ip)):
    return {"admin": "panel", "your_ip": ip}
```

---

## 🎯 Next Steps

1. ✅ Run the API and test all endpoints
2. ✅ Read the code in `03_dependency_injection.py`
3. ✅ Try modifying rate limits
4. ✅ Add your own custom dependency
5. ✅ Explore dependency overrides for testing

---

## 📚 Additional Resources

- [FastAPI Dependencies Docs](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Dependency Injection in Python](https://python-dependency-injector.ets-labs.org/)
- [Testing with Dependency Overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/)

---

**Happy Learning! 🚀**
