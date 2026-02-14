# 📋 FastAPI Dependency Injection - Quick Reference

## Basic Syntax

```python
from fastapi import Depends

def my_dependency():
    return "value"

@app.get("/")
def endpoint(result = Depends(my_dependency)):
    return {"result": result}
```

---

## 🔧 Three Types of Dependencies

### 1️⃣ Function-Based Dependencies

**Use for:** Simple logic, authentication, validation

```python
def get_token(token: str = Header(...)):
    if token != "valid":
        raise HTTPException(401, "Invalid token")
    return token

@app.get("/protected")
def protected(token: str = Depends(get_token)):
    return {"token": token}
```

### 2️⃣ Class-Based Dependencies

**Use for:** Complex logic, configurable dependencies, stateful operations

```python
class RateLimiter:
    def __init__(self, requests: int):
        self.max = requests
    
    def __call__(self, request: Request):
        # Check rate limit
        return {"remaining": self.max}

# Create instances
limiter_5 = RateLimiter(5)
limiter_10 = RateLimiter(10)

@app.post("/create")
def create(rate = Depends(limiter_5)):  # 5 req limit
    pass

@app.get("/read")
def read(rate = Depends(limiter_10)):  # 10 req limit
    pass
```

### 3️⃣ Generator-Based Dependencies (with cleanup)

**Use for:** Resources that need cleanup (DB, files, connections)

```python
def get_db():
    db = Database()     # Setup
    try:
        yield db        # Use (this is injected)
    finally:
        db.close()      # Cleanup (always runs)

@app.get("/users")
def get_users(db = Depends(get_db)):
    return db.query_all()
    # db.close() called automatically here
```

---

## 🔗 Dependency Chaining

Dependencies can depend on other dependencies:

```python
# Level 1: Get user
def get_user(token: str = Header(...)):
    return {"id": 1, "role": "user"}

# Level 2: Check admin (depends on get_user)
def require_admin(user = Depends(get_user)):
    if user["role"] != "admin":
        raise HTTPException(403, "Admin required")
    return user

# Endpoint uses require_admin (automatically calls get_user)
@app.delete("/users/{id}")
def delete_user(id: int, admin = Depends(require_admin)):
    return {"deleted": id}
```

---

## 📚 Common Patterns

### Authentication

```python
def verify_token(token: str = Header(...)):
    if token not in valid_tokens:
        raise HTTPException(401, "Unauthorized")
    return tokens[token]

@app.get("/me")
def current_user(user = Depends(verify_token)):
    return user
```

### Authorization (Chained)

```python
def require_admin(user = Depends(verify_token)):  # Chains verify_token
    if user["role"] != "admin":
        raise HTTPException(403, "Forbidden")
    return user
```

### Database Session

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Logging

```python
def log_request(request: Request):
    logger.info(f"{request.method} {request.url.path}")
    return {"logged": True}
```

### Rate Limiting

```python
class RateLimiter:
    def __init__(self, limit: int):
        self.limit = limit
        self.requests = {}
    
    def __call__(self, request: Request):
        ip = request.client.host
        # Check if exceeded...
        return {"remaining": remaining}
```

---

## 🎯 Combining Multiple Dependencies

```python
@app.post("/items")
def create_item(
    item: Item,                              # Request body
    user = Depends(verify_token),           # Auth
    rate = Depends(rate_limiter),           # Rate limit
    log = Depends(log_request),             # Logging
    db = Depends(get_db),                   # Database
):
    # All dependencies run before this code
    pass
```

**Execution Order:** Dependencies run in the order declared!

---

## 💡 Using `Annotated` (Cleaner Code)

Instead of repeating `Depends()`:

```python
from typing import Annotated

# Define type aliases
CurrentUser = Annotated[dict, Depends(get_current_user)]
DB = Annotated[Session, Depends(get_db)]
RateLimit = Annotated[dict, Depends(rate_limiter)]

# Use in endpoints
@app.get("/users")
def list_users(
    user: CurrentUser,    # Much cleaner!
    db: DB,
    rate: RateLimit
):
    pass
```

---

## 🧪 Testing with Dependency Overrides

Override dependencies in tests:

```python
# Real dependency
def get_real_db():
    return RealDatabase()

# Test dependency
def get_fake_db():
    return FakeDatabase()

# In tests
app.dependency_overrides[get_real_db] = get_fake_db

# All endpoints now use FakeDatabase!
```

---

## ⚡ Quick Comparison

| Feature | Function | Class | Generator |
|---------|----------|-------|-----------|
| Simple logic | ✅ Best | ❌ | ❌ |
| Configurable | ⚠️ Possible | ✅ Best | ⚠️ Possible |
| Cleanup needed | ❌ | ❌ | ✅ Best |
| State management | ❌ | ✅ | ⚠️ Per-request |
| Reusability | ✅ | ✅✅ | ✅ |

---

## 🎓 When to Use What

| Use Case | Best Choice | Example |
|----------|-------------|---------|
| Authentication | Function | `verify_token()` |
| Authorization | Function (chained) | `require_admin()` |
| Rate Limiting | Class | `RateLimiter()` |
| Database | Generator | `get_db()` |
| Logging | Class or Function | `LogRequest()` |
| Caching | Class | `Cache()` |
| Configuration | Function | `get_settings()` |

---

## 🚀 Common Mistakes to Avoid

### ❌ Wrong: Forgetting to call class instances

```python
class MyDep:
    def __call__(self):
        return "value"

@app.get("/")
def endpoint(x = Depends(MyDep)):  # ❌ Wrong! Should be MyDep()
    pass
```

### ✅ Correct:

```python
my_dep = MyDep()  # Create instance

@app.get("/")
def endpoint(x = Depends(my_dep)):  # ✅ Correct!
    pass
```

### ❌ Wrong: Using `return` instead of `yield` for cleanup

```python
def get_db():
    db = connect()
    return db      # ❌ Won't cleanup!
    db.close()     # Never runs!
```

### ✅ Correct:

```python
def get_db():
    db = connect()
    try:
        yield db   # ✅ Correct!
    finally:
        db.close() # Always runs
```

---

## 📖 Next Steps

1. ✅ Run `03_dependency_injection.py`
2. ✅ Test with `test_dependency_injection.py`
3. ✅ Read full tutorial: `03_DI_TUTORIAL.md`
4. ✅ Experiment with the code
5. ✅ Create your own dependencies

---

## 🔍 Debug Tips

### See dependency execution order:

```python
def dep1():
    print("Dep 1 runs")
    return 1

def dep2():
    print("Dep 2 runs")
    return 2

@app.get("/")
def endpoint(a = Depends(dep1), b = Depends(dep2)):
    print("Endpoint runs")
    return {"a": a, "b": b}
```

**Output:**
```
Dep 1 runs
Dep 2 runs
Endpoint runs
```

---

**Happy Learning! 🚀**
