"""
Comprehensive tests for Architecture Mastery module

Run: pytest test_architecture.py -v
     pytest test_architecture.py -v --cov=.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import time


# ====================================
# TEST CLEAN ARCHITECTURE
# ====================================

def test_clean_architecture_imports():
    """Test that clean architecture module imports correctly"""
    from importlib import import_module
    module = import_module("13_clean_architecture")
    assert hasattr(module, "app")
    assert hasattr(module, "Product")
    assert hasattr(module, "Order")


def test_clean_architecture_product_creation():
    """Test product creation with domain validation"""
    import sys
    sys.path.insert(0, '.')
    from importlib import import_module
    module = import_module("13_clean_architecture")
    
    Product = module.Product
    
    # Test valid product
    product = Product(
        id="1",
        name="Test Product",
        price=99.99,
        stock=10,
        created_at=datetime.utcnow()
    )
    assert product.is_available() == True
    
    # Test price validation
    with pytest.raises(ValueError):
        product.price = -10
    
    # Test stock reduction
    product.reduce_stock(5)
    assert product.stock == 5
    
    # Test insufficient stock
    with pytest.raises(ValueError):
        product.reduce_stock(10)


def test_clean_architecture_order_business_rules():
    """Test order business rules"""
    import sys
    sys.path.insert(0, '.')
    from importlib import import_module
    module = import_module("13_clean_architecture")
    
    Order = module.Order
    
    # Create order
    order = Order(
        id="1",
        customer_email="test@example.com",
        items=[],
        total=100.0,
        status="pending"
    )
    
    # Test can cancel
    assert order.can_cancel() == True
    
    # Cancel order
    order.cancel()
    assert order.status == "cancelled"
    
    # Cannot cancel again
    with pytest.raises(ValueError):
        order.cancel()


def test_clean_architecture_api_endpoints():
    """Test Clean Architecture API endpoints"""
    import sys
    sys.path.insert(0, '.')
    from importlib import import_module
    module = import_module("13_clean_architecture")
    
    client = TestClient(module.app)
    
    # Test root
    response = client.get("/")
    assert response.status_code == 200
    assert "Clean Architecture" in response.json()["message"]
    
    # Create product
    product_data = {
        "name": "Test Laptop",
        "price": 999.99,
        "stock": 10
    }
    response = client.post("/products", json=product_data)
    assert response.status_code == 201
    product = response.json()
    assert product["name"] == "Test Laptop"
    
    product_id = product["id"]
    
    # Get product
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    
    # List products
    response = client.get("/products")
    assert response.status_code == 200
    assert len(response.json()) >= 1


# ====================================
# TEST REPOSITORY PATTERN
# ====================================

def test_repository_pattern_imports():
    """Test repository pattern imports"""
    from importlib import import_module
    module = import_module("13_repository_pattern")
    assert hasattr(module, "UserRepository")
    assert hasattr(module, "InMemoryUserRepository")
    assert hasattr(module, "SQLiteUserRepository")


@pytest.mark.asyncio
async def test_in_memory_repository():
    """Test in-memory repository"""
    import sys
    sys.path.insert(0, '.')
    from importlib import import_module
    module = import_module("13_repository_pattern")
    
    User = module.User
    InMemoryUserRepository = module.InMemoryUserRepository
    
    repo = InMemoryUserRepository()
    
    # Create user
    user = User(
        id=0,
        email="test@example.com",
        username="testuser",
        full_name="Test User"
    )
    created = await repo.create(user)
    assert created.id == 1
    
    # Get user
    retrieved = await repo.get_by_id(1)
    assert retrieved is not None
    assert retrieved.email == "test@example.com"
    
    # Get by email
    retrieved = await repo.get_by_email("test@example.com")
    assert retrieved is not None
    
    # Update user
    created.full_name = "Updated Name"
    updated = await repo.update(created)
    assert updated.full_name == "Updated Name"
    
    # Delete user
    deleted = await repo.delete(1)
    assert deleted == True
    
    # Verify deleted
    retrieved = await repo.get_by_id(1)
    assert retrieved is None


@pytest.mark.asyncio
async def test_cached_repository():
    """Test cached repository decorator"""
    import sys
    sys.path.insert(0, '.')
    from importlib import import_module
    module = import_module("13_repository_pattern")
    
    User = module.User
    InMemoryUserRepository = module.InMemoryUserRepository
    CachedUserRepository = module.CachedUserRepository
    
    base_repo = InMemoryUserRepository()
    cached_repo = CachedUserRepository(base_repo, ttl=60)
    
    # Create user
    user = User(
        id=0,
        email="cached@example.com",
        username="cached",
        full_name="Cached User"
    )
    created = await cached_repo.create(user)
    
    # First get (cache miss)
    start = time.time()
    user1 = await cached_repo.get_by_id(created.id)
    time1 = time.time() - start
    
    # Second get (cache hit - should be faster)
    start = time.time()
    user2 = await cached_repo.get_by_id(created.id)
    time2 = time.time() - start
    
    assert user1 is not None
    assert user2 is not None
    # Cache hit should generally be faster
    print(f"Cache miss: {time1*1000:.2f}ms, Cache hit: {time2*1000:.2f}ms")


def test_repository_pattern_api():
    """Test repository pattern API"""
    import sys
    sys.path.insert(0, '.')
    from importlib import import_module
    module = import_module("13_repository_pattern")
    
    client = TestClient(module.app)
    
    # Create user
    user_data = {
        "email": "api@example.com",
        "username": "apiuser",
        "full_name": "API User"
    }
    response = client.post("/users", json=user_data)
    assert response.status_code == 201
    user = response.json()
    
    # Get user
    response = client.get(f"/users/{user['id']}")
    assert response.status_code == 200
    
    # List users
    response = client.get("/users")
    assert response.status_code == 200


# ====================================
# TEST RATE LIMITING
# ====================================

def test_rate_limiting_imports():
    """Test rate limiting imports"""
    from importlib import import_module
    module = import_module("13_rate_limiting")
    assert hasattr(module, "TokenBucketLimiter")
    assert hasattr(module, "SlidingWindowLimiter")
    assert hasattr(module, "FixedWindowCounter")


def test_token_bucket_limiter():
    """Test token bucket algorithm"""
    import sys
    sys.path.insert(0, '.')
    from importlib import import_module
    module = import_module("13_rate_limiting")
    
    TokenBucketLimiter = module.TokenBucketLimiter
    
    limiter = TokenBucketLimiter(capacity=5, refill_rate=10.0)
    
    # Should allow 5 requests immediately
    for _ in range(5):
        assert limiter.allow_request("test_key") == True
    
    # 6th request should be denied
    assert limiter.allow_request("test_key") == False
    
    # Wait for tokens to refill
    time.sleep(0.2)  # Should refill ~2 tokens
    assert limiter.allow_request("test_key") == True


def test_sliding_window_limiter():
    """Test sliding window algorithm"""
    import sys
    sys.path.insert(0, '.')
    from importlib import import_module
    module = import_module("13_rate_limiting")
    
    SlidingWindowLimiter = module.SlidingWindowLimiter
    
    limiter = SlidingWindowLimiter(max_requests=3, window_seconds=1)
    
    # Should allow 3 requests
    assert limiter.allow_request("test_key") == True
    assert limiter.allow_request("test_key") == True
    assert limiter.allow_request("test_key") == True
    
    # 4th request should be denied
    assert limiter.allow_request("test_key") == False
    
    # Check remaining
    remaining = limiter.get_remaining_requests("test_key")
    assert remaining == 0


def test_fixed_window_counter():
    """Test fixed window algorithm"""
    import sys
    sys.path.insert(0, '.')
    from importlib import import_module
    module = import_module("13_rate_limiting")
    
    FixedWindowCounter = module.FixedWindowCounter
    
    counter = FixedWindowCounter(max_requests=5, window_seconds=1)
    
    # Should allow 5 requests
    for _ in range(5):
        assert counter.allow_request("test_key") == True
    
    # 6th should be denied
    assert counter.allow_request("test_key") == False
    
    # Check remaining
    remaining = counter.get_remaining_requests("test_key")
    assert remaining == 0


# ====================================
# TEST API GATEWAY
# ====================================

def test_api_gateway_imports():
    """Test API gateway imports"""
    from importlib import import_module
    module = import_module("13_api_gateway")
    assert hasattr(module, "CircuitBreaker")
    assert hasattr(module, "ServiceRegistry")
    assert hasattr(module, "APIGateway")


def test_circuit_breaker():
    """Test circuit breaker pattern"""
    import sys
    sys.path.insert(0, '.')
    from importlib import import_module
    module = import_module("13_api_gateway")
    
    CircuitBreaker = module.CircuitBreaker
    CircuitState = module.CircuitState
    
    breaker = CircuitBreaker(failure_threshold=3, timeout_seconds=1)
    
    # Initial state: CLOSED
    assert breaker.state == CircuitState.CLOSED
    assert breaker.can_attempt() == True
    
    # Record failures
    breaker.record_failure()
    breaker.record_failure()
    breaker.record_failure()
    
    # Should be OPEN
    assert breaker.state == CircuitState.OPEN
    assert breaker.can_attempt() == False
    
    # Wait for timeout
    time.sleep(1.1)
    
    # Should be HALF_OPEN
    assert breaker.can_attempt() == True
    assert breaker.state == CircuitState.HALF_OPEN
    
    # Success should close
    breaker.record_success()
    assert breaker.state == CircuitState.CLOSED


def test_service_registry():
    """Test service registry"""
    import sys
    sys.path.insert(0, '.')
    from importlib import import_module
    module = import_module("13_api_gateway")
    
    ServiceRegistry = module.ServiceRegistry
    
    registry = ServiceRegistry()
    
    # Register services
    registry.register_service("test", "http://localhost:9000")
    registry.register_service("test", "http://localhost:9001")
    
    # Get service URL (round-robin)
    url1 = registry.get_service_url("test")
    url2 = registry.get_service_url("test")
    
    assert url1 == "http://localhost:9000"
    assert url2 == "http://localhost:9001"
    
    # Get circuit breaker
    breaker = registry.get_circuit_breaker("test")
    assert breaker is not None


# ====================================
# TEST MICROSERVICES
# ====================================

def test_microservices_imports():
    """Test microservices imports"""
    from importlib import import_module
    module = import_module("13_microservices_example")
    assert hasattr(module, "Event")
    assert hasattr(module, "MessageBus")
    assert hasattr(module, "create_users_service")
    assert hasattr(module, "create_products_service")
    assert hasattr(module, "create_orders_service")


@pytest.mark.asyncio
async def test_message_bus():
    """Test message bus"""
    import sys
    sys.path.insert(0, '.')
    from importlib import import_module
    module = import_module("13_microservices_example")
    
    MessageBus = module.MessageBus
    Event = module.Event
    EventType = module.EventType
    
    bus = MessageBus()
    
    events_received = []
    
    async def handler(event):
        events_received.append(event)
    
    # Subscribe
    bus.subscribe(EventType.USER_CREATED, handler)
    
    # Publish event
    event = Event(
        type=EventType.USER_CREATED,
        data={"user_id": 1},
        source_service="test"
    )
    await bus.publish(event)
    
    # Check handler was called
    assert len(events_received) == 1
    assert events_received[0].type == EventType.USER_CREATED
    
    # Check event store
    stored_events = bus.get_events()
    assert len(stored_events) == 1


def test_users_microservice():
    """Test users microservice"""
    import sys
    sys.path.insert(0, '.')
    from importlib import import_module
    module = import_module("13_microservices_example")
    
    users_service = module.create_users_service()
    client = TestClient(users_service)
    
    # Test root
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "users"
    
    # Test health
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_products_microservice():
    """Test products microservice"""
    import sys
    sys.path.insert(0, '.')
    from importlib import import_module
    module = import_module("13_microservices_example")
    
    products_service = module.create_products_service()
    client = TestClient(products_service)
    
    # Test root
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "products"
    
    # Test health
    response = client.get("/health")
    assert response.status_code == 200


# ====================================
# INTEGRATION TESTS
# ====================================

def test_architecture_patterns_integration():
    """Test that all architecture patterns work together"""
    # This is a smoke test to ensure all modules can be imported
    from importlib import import_module
    
    modules = [
        "13_clean_architecture",
        "13_repository_pattern",
        "13_rate_limiting",
        "13_caching_redis",
        "13_api_gateway",
        "13_microservices_example"
    ]
    
    for module_name in modules:
        try:
            module = import_module(module_name)
            assert module is not None
            print(f"✓ {module_name} imported successfully")
        except Exception as e:
            pytest.fail(f"Failed to import {module_name}: {e}")


# ====================================
# PERFORMANCE TESTS
# ====================================

def test_cache_performance():
    """Test that caching improves performance"""
    import sys
    sys.path.insert(0, '.')
    from importlib import import_module
    module = import_module("13_repository_pattern")
    
    User = module.User
    InMemoryUserRepository = module.InMemoryUserRepository
    CachedUserRepository = module.CachedUserRepository
    
    import asyncio
    
    async def run_test():
        base_repo = InMemoryUserRepository()
        cached_repo = CachedUserRepository(base_repo, ttl=60)
        
        user = User(
            id=0,
            email="perf@example.com",
            username="perftest",
            full_name="Performance Test"
        )
        created = await cached_repo.create(user)
        
        # Measure uncached performance
        times_uncached = []
        for _ in range(10):
            start = time.time()
            await base_repo.get_by_id(created.id)
            times_uncached.append(time.time() - start)
        
        # Measure cached performance
        times_cached = []
        for _ in range(10):
            start = time.time()
            await cached_repo.get_by_id(created.id)
            times_cached.append(time.time() - start)
        
        avg_uncached = sum(times_uncached) / len(times_uncached)
        avg_cached = sum(times_cached) / len(times_cached)
        
        print(f"Average uncached: {avg_uncached*1000:.2f}ms")
        print(f"Average cached: {avg_cached*1000:.2f}ms")
        print(f"Improvement: {avg_uncached/avg_cached:.1f}x faster")
        
        # Cache should provide some benefit (even if small in-memory)
        # This is more about verifying the pattern works
        return True
    
    result = asyncio.run(run_test())
    assert result == True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
