# 13. Architecture Mastery

## Overview

This module covers advanced architectural patterns and best practices for building scalable, maintainable, and production-ready FastAPI applications. You'll learn clean architecture principles, layered structures, repository patterns, microservices architecture, API gateways, rate limiting, and caching strategies.

## Topics Covered

1. **Clean Architecture** - Separation of concerns with clear boundaries
2. **Layered Structure** - Presentation, Business, Data layers
3. **Service Layer** - Business logic encapsulation
4. **Repository Pattern** - Data access abstraction
5. **API Gateway** - Single entry point for microservices
6. **Rate Limiting** - Protect APIs from abuse
7. **Redis Caching** - Performance optimization
8. **Microservices** - Distributed architecture patterns

## Files in This Module

- `13_clean_architecture.py` - Complete clean architecture implementation
- `13_repository_pattern.py` - Repository pattern with multiple backends
- `13_service_layer.py` - Service layer with business logic
- `13_rate_limiting.py` - Rate limiting strategies
- `13_caching_redis.py` - Redis caching implementation
- `13_api_gateway.py` - API gateway pattern
- `13_microservices_example.py` - Microservices architecture
- `test_architecture.py` - Comprehensive tests
- `manual_test.py` - Manual testing examples
- `ARCHITECTURE_CHEATSHEET.md` - Quick reference guide

## Architecture Principles

### Clean Architecture Layers

```
┌─────────────────────────────────────┐
│   Presentation Layer (API/Routes)   │
├─────────────────────────────────────┤
│   Application Layer (Services)      │
├─────────────────────────────────────┤
│   Domain Layer (Business Logic)     │
├─────────────────────────────────────┤
│   Infrastructure Layer (Data/Cache) │
└─────────────────────────────────────┘
```

### Dependency Rule

- Outer layers depend on inner layers
- Inner layers know nothing about outer layers
- Domain layer has no external dependencies
- Business logic is isolated from frameworks

## Quick Start

```bash
# Install dependencies
pip install fastapi uvicorn redis slowapi

# Start Redis (required for caching examples)
docker run -d -p 6379:6379 redis:alpine

# Run examples
./quickstart.sh

# Run tests
pytest test_architecture.py -v
```

## Key Concepts

### 1. Repository Pattern

Abstracts data access logic from business logic:

```python
# Abstract interface
class UserRepository(ABC):
    @abstractmethod
    async def get(self, user_id: int) -> User:
        pass

# Concrete implementations
class SQLUserRepository(UserRepository):
    async def get(self, user_id: int) -> User:
        # Database implementation
        pass

class CachedUserRepository(UserRepository):
    async def get(self, user_id: int) -> User:
        # Check cache, then database
        pass
```

### 2. Service Layer

Encapsulates business logic:

```python
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    async def create_user(self, data: CreateUser) -> User:
        # Business validation
        # Call repository
        # Return result
        pass
```

### 3. Dependency Injection

Wire components together:

```python
def get_repository() -> UserRepository:
    return SQLUserRepository(database)

def get_service(repo: UserRepository = Depends(get_repository)) -> UserService:
    return UserService(repo)

@app.post("/users")
async def create_user(
    data: CreateUser,
    service: UserService = Depends(get_service)
):
    return await service.create_user(data)
```

## Benefits of Clean Architecture

1. **Testability** - Easy to mock dependencies
2. **Maintainability** - Clear separation of concerns
3. **Flexibility** - Easy to swap implementations
4. **Scalability** - Can evolve with requirements
5. **Independence** - Business logic independent of frameworks

## Rate Limiting Strategies

### 1. Fixed Window

```python
# 100 requests per hour
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/data")
@limiter.limit("100/hour")
async def get_data():
    return {"data": "value"}
```

### 2. Token Bucket

```python
# Allows burst traffic with gradual replenishment
@app.get("/api/data")
@limiter.limit("10/second;100/minute")
async def get_data():
    return {"data": "value"}
```

### 3. Sliding Window

```python
# More accurate than fixed window
# Counts requests in rolling time window
```

## Caching Strategies

### 1. Cache-Aside (Lazy Loading)

```python
async def get_user(user_id: int):
    # Check cache first
    cached = await redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    
    # Cache miss - fetch from database
    user = await db.get_user(user_id)
    await redis.set(f"user:{user_id}", json.dumps(user), ex=3600)
    return user
```

### 2. Write-Through

```python
async def update_user(user_id: int, data: dict):
    # Update database
    user = await db.update_user(user_id, data)
    
    # Update cache
    await redis.set(f"user:{user_id}", json.dumps(user), ex=3600)
    return user
```

### 3. Write-Behind (Write-Back)

```python
async def update_user(user_id: int, data: dict):
    # Update cache immediately
    await redis.set(f"user:{user_id}", json.dumps(data))
    
    # Queue database update
    await task_queue.enqueue(db.update_user, user_id, data)
```

## Microservices Patterns

### 1. Service Discovery

Each service registers itself and discovers other services

### 2. Circuit Breaker

Prevent cascading failures in distributed systems

### 3. API Gateway

Single entry point that routes to multiple services

### 4. Event-Driven Communication

Services communicate via message queues

## Best Practices

1. **Keep layers independent** - Use interfaces/abstractions
2. **Single Responsibility** - Each class does one thing
3. **Dependency Inversion** - Depend on abstractions, not concrete classes
4. **Fail Fast** - Validate early, fail with clear errors
5. **Monitor Everything** - Logging, metrics, tracing
6. **Cache Wisely** - Not everything needs caching
7. **Rate Limit Appropriately** - Balance protection and usability
8. **Use Async Where It Matters** - I/O operations, not CPU tasks

## Common Pitfalls

❌ **Over-Engineering** - Don't add layers you don't need
❌ **Tight Coupling** - Avoid direct dependencies on frameworks
❌ **Ignoring Cache Invalidation** - Stale data is worse than no cache
❌ **No Monitoring** - Can't fix what you can't see
❌ **Synchronous Code in Async** - Blocks event loop
❌ **No Rate Limiting** - Vulnerable to abuse
❌ **Premature Microservices** - Start monolith, split when needed

## Production Checklist

- [ ] Proper layering and separation of concerns
- [ ] Repository pattern for data access
- [ ] Service layer for business logic
- [ ] Dependency injection configured
- [ ] Rate limiting on public endpoints
- [ ] Caching for expensive operations
- [ ] Health check endpoints
- [ ] Logging and monitoring
- [ ] Error handling and recovery
- [ ] Documentation (OpenAPI)
- [ ] Load testing completed
- [ ] Security audit passed

## Further Reading

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Repository Pattern](https://deviq.com/design-patterns/repository-pattern)
- [Microservices Patterns](https://microservices.io/patterns/index.html)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [FastAPI Performance Tips](https://fastapi.tiangolo.com/deployment/concepts/)

## Next Steps

After mastering these architecture patterns:
- Explore event sourcing and CQRS
- Study domain-driven design (DDD)
- Learn about service mesh (Istio, Linkerd)
- Practice with real-world projects
- Contribute to open-source projects

---

**Remember**: Good architecture enables change. The best architecture is the simplest one that meets your current needs while allowing for future growth.
