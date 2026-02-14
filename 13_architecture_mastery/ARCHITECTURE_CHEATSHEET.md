# Architecture Mastery Cheatsheet

## Clean Architecture Layers

```
┌─────────────────────────────────────┐
│   Presentation (Routes/Controllers) │
├─────────────────────────────────────┤
│   Application (Services/Use Cases)  │
├─────────────────────────────────────┤
│   Domain (Business Logic/Entities)  │
├─────────────────────────────────────┤
│   Infrastructure (Data/External)    │
└─────────────────────────────────────┘
```

**Key Principles:**
- Outer layers depend on inner layers (never reverse)
- Domain layer has zero external dependencies
- Use interfaces/protocols for abstraction
- Business rules isolated from frameworks

## Repository Pattern

### Basic Structure
```python
# Interface (Port)
class UserRepository(Protocol):
    async def get(self, id: int) -> Optional[User]: ...
    async def save(self, user: User) -> User: ...

# Implementation (Adapter)
class SQLUserRepository(UserRepository):
    async def get(self, id: int) -> Optional[User]:
        # Database implementation
        pass
```

### Benefits
- ✅ Easy to swap data sources
- ✅ Simple to mock for testing
- ✅ Centralized data access logic
- ✅ Consistent interface

## Service Layer

### Purpose
Encapsulates business logic and orchestrates domain operations

```python
class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
    
    async def create_user(self, data: CreateUserDTO) -> User:
        # Business validation
        if await self.repo.get_by_email(data.email):
            raise ValueError("Email exists")
        
        # Create domain entity
        user = User(**data.dict())
        
        # Persist
        return await self.repo.save(user)
```

**What Goes in Service Layer:**
- Business validation
- Domain entity orchestration
- Transaction management
- Event publishing

**What Doesn't:**
- ❌ HTTP request/response handling
- ❌ Database queries (use repository)
- ❌ Business rules (use domain entities)

## Rate Limiting Strategies

### 1. Fixed Window
```python
# Simple, but can burst at boundaries
@app.get("/api/data")
@limiter.limit("100/hour")
async def get_data():
    return {"data": "value"}
```

**Pros:** Simple, memory efficient  
**Cons:** Burst at window boundaries

### 2. Sliding Window
```python
# More accurate, tracks each request timestamp
class SlidingWindowLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.requests = deque()  # Timestamps
```

**Pros:** Accurate, no boundary bursts  
**Cons:** More memory (stores timestamps)

### 3. Token Bucket
```python
# Allows controlled bursts
class TokenBucketLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens/second
```

**Pros:** Allows bursts, natural rate control  
**Cons:** More complex implementation

### Quick Comparison

| Strategy | Accuracy | Memory | Bursts | Complexity |
|----------|----------|--------|--------|------------|
| Fixed Window | Low | Low | ⚠️ High | Simple |
| Sliding Window | High | Medium | ✅ Controlled | Medium |
| Token Bucket | High | Low | ✅ Allowed | Medium |

## Caching Patterns

### 1. Cache-Aside (Lazy Loading)
```python
async def get_user(user_id: int):
    # Check cache
    cached = await redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    
    # Query database
    user = await db.get_user(user_id)
    
    # Store in cache
    await redis.set(f"user:{user_id}", json.dumps(user), ex=300)
    return user
```

**Use When:** Read-heavy workloads, data rarely changes

### 2. Write-Through
```python
async def update_user(user_id: int, data: dict):
    # Update database
    user = await db.update_user(user_id, data)
    
    # Update cache immediately
    await redis.set(f"user:{user_id}", json.dumps(user), ex=300)
    return user
```

**Use When:** Need cache consistency, write latency acceptable

### 3. Write-Behind (Write-Back)
```python
async def update_user(user_id: int, data: dict):
    # Update cache immediately
    await redis.set(f"user:{user_id}", json.dumps(data))
    
    # Queue database update
    await queue.enqueue(db.update_user, user_id, data)
```

**Use When:** Write-heavy, can tolerate data loss risk

### Cache Invalidation Strategies

```python
# 1. Time-based (TTL)
await redis.set(key, value, ex=300)  # 5 minutes

# 2. Event-based
async def on_user_update(user_id):
    await redis.delete(f"user:{user_id}")

# 3. Pattern-based
await redis.delete("users:*")  # All user caches
```

## API Gateway Pattern

### Core Responsibilities
```
┌─────────────────┐
│  API Gateway    │
├─────────────────┤
│ • Routing       │
│ • Auth          │
│ • Rate Limiting │
│ • Transform     │
│ • Aggregation   │
│ • Circuit Break │
└────────┬────────┘
         │
    ┌────┴─────┐
    │   │   │   │
 Service A B C D
```

### Basic Implementation
```python
async def proxy_request(service: str, path: str):
    service_url = get_service_url(service)
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{service_url}{path}")
        return response.json()
```

### Circuit Breaker
```python
class CircuitBreaker:
    CLOSED → OPEN (failures > threshold)
    OPEN → HALF_OPEN (timeout elapsed)
    HALF_OPEN → CLOSED (success)
```

## Microservices Patterns

### 1. Service Communication

**Synchronous (HTTP/gRPC):**
```python
# Direct HTTP call
async with httpx.AsyncClient() as client:
    response = await client.get("http://user-service/users/1")
```

**Asynchronous (Events):**
```python
# Publish event
await message_bus.publish(Event(
    type="ORDER_CREATED",
    data={"order_id": order.id}
))
```

### 2. Saga Pattern (Distributed Transactions)

```python
async def create_order(order_data):
    try:
        # 1. Reserve inventory
        await inventory_service.reserve(order_data.items)
        
        # 2. Process payment
        await payment_service.charge(order_data.amount)
        
        # 3. Create order
        order = await order_service.create(order_data)
        
        return order
    except Exception:
        # Compensating transactions
        await inventory_service.release(order_data.items)
        await payment_service.refund(order_data.amount)
        raise
```

### 3. Service Discovery

```python
class ServiceRegistry:
    def register(self, name: str, url: str): ...
    def discover(self, name: str) -> str: ...
    def health_check(self): ...
```

## Dependency Injection

### FastAPI Pattern
```python
# Repository
def get_repository() -> UserRepository:
    return SQLUserRepository(db)

# Service
def get_service(
    repo: UserRepository = Depends(get_repository)
) -> UserService:
    return UserService(repo)

# Route
@app.post("/users")
async def create_user(
    data: CreateUserRequest,
    service: UserService = Depends(get_service)
):
    return await service.create_user(data)
```

## Testing Patterns

### 1. Mock Repository
```python
class MockUserRepository(UserRepository):
    def __init__(self):
        self.users = {}
    
    async def save(self, user: User) -> User:
        self.users[user.id] = user
        return user
```

### 2. Test with DI Override
```python
def test_create_user():
    app.dependency_overrides[get_repository] = lambda: MockUserRepository()
    
    response = client.post("/users", json={...})
    assert response.status_code == 201
```

## Performance Optimization

### 1. Database
- Use connection pooling
- Index frequently queried fields
- Implement pagination
- Use SELECT specific fields

### 2. Caching
- Cache expensive queries
- Use appropriate TTL
- Invalidate on writes
- Monitor hit rate

### 3. Async Operations
```python
# Parallel requests
results = await asyncio.gather(
    get_user(user_id),
    get_orders(user_id),
    get_products()
)
```

### 4. Background Tasks
```python
@app.post("/users")
async def create_user(
    data: UserData,
    background_tasks: BackgroundTasks
):
    user = await create_user_sync(data)
    background_tasks.add_task(send_welcome_email, user.email)
    return user
```

## Security Best Practices

### 1. Authentication
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> User:
    payload = jwt.decode(token, SECRET_KEY)
    user = await get_user(payload["sub"])
    if not user:
        raise HTTPException(401)
    return user
```

### 2. Rate Limiting
- Public endpoints: 10-100 req/min
- Authenticated: 1000 req/min
- Admin: Unlimited or separate limit

### 3. Input Validation
```python
class CreateUserRequest(BaseModel):
    email: EmailStr  # Validated email
    username: str = Field(..., min_length=3, max_length=50)
    age: int = Field(..., ge=18, le=120)
```

## Monitoring & Observability

### 1. Health Checks
```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": await check_db(),
        "cache": await check_redis(),
        "timestamp": datetime.utcnow()
    }
```

### 2. Metrics
- Request count
- Response time (p50, p95, p99)
- Error rate
- Cache hit rate
- Active connections

### 3. Logging
```python
import logging

logger = logging.getLogger(__name__)

@app.post("/users")
async def create_user(data: UserData):
    logger.info(f"Creating user: {data.email}")
    try:
        user = await service.create_user(data)
        logger.info(f"User created: {user.id}")
        return user
    except Exception as e:
        logger.error(f"User creation failed: {e}")
        raise
```

## Quick Commands

```bash
# Start Redis (for caching)
docker run -d -p 6379:6379 redis:alpine

# Run with auto-reload
uvicorn main:app --reload

# Run on specific port
uvicorn main:app --port 8000

# Run multiple workers
uvicorn main:app --workers 4

# Run tests
pytest test_*.py -v

# Check test coverage
pytest --cov=. --cov-report=html

# Load test
hey -n 1000 -c 10 http://localhost:8000/api/endpoint
```

## Common Pitfalls

❌ **Over-engineering** - Don't add layers you don't need  
❌ **Tight coupling** - Depend on abstractions, not concrete classes  
❌ **No caching strategy** - Cache without invalidation = stale data  
❌ **Sync in async** - Blocking operations in async functions  
❌ **No rate limiting** - Open to abuse and DDoS  
❌ **Poor error handling** - Expose internal errors to users  
❌ **No monitoring** - Can't fix what you can't see  

## Architecture Decision Matrix

| If you need... | Use... |
|----------------|--------|
| Data abstraction | Repository Pattern |
| Business logic separation | Service Layer |
| Prevent abuse | Rate Limiting |
| Speed up reads | Caching (Cache-Aside) |
| Multiple services | API Gateway |
| Distributed system | Microservices |
| Prevent cascading failures | Circuit Breaker |
| Async communication | Message Bus/Events |

## Resources

- [Martin Fowler - Microservices](https://martinfowler.com/articles/microservices.html)
- [Clean Architecture Book](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Microservices Patterns](https://microservices.io/patterns/index.html)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
