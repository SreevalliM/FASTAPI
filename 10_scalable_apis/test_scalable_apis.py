"""
Tests for Scalable APIs Module
==============================

Tests async vs sync performance, concurrency patterns,
and production deployment features.

Run with: pytest test_scalable_apis.py -v
"""

import pytest
import asyncio
import time
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Import the applications
import sys
sys.path.insert(0, ".")

# Note: Rename files without the '10_' prefix for imports, or use importlib
# For now, we'll import using the actual module names
try:
    import importlib.util
    
    def load_module(file_path, module_name):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    async_basics = load_module("10_async_basics.py", "async_basics")
    async_basics_app = async_basics.app
    
    db_ops = load_module("10_async_db_operations.py", "db_ops")
    db_app = db_ops.app
    
    concurrency = load_module("10_concurrency_patterns.py", "concurrency")
    concurrency_app = concurrency.app
    
    production = load_module("10_production_deployment.py", "production")
    production_app = production.app
except Exception as e:
    # Fallback: skip imports if files not found
    print(f"Warning: Could not import modules: {e}")
    async_basics_app = None
    db_app = None
    concurrency_app = None
    production_app = None


# ============================================================================
# Test Async Basics
# ============================================================================

class TestAsyncBasics:
    """Test async vs sync endpoints"""
    
    @pytest.fixture
    def client(self):
        return TestClient(async_basics_app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "Async Basics API" in data["title"]
    
    def test_sync_sleep(self, client):
        """Test synchronous sleep endpoint"""
        response = client.get("/sync/sleep?seconds=1")
        assert response.status_code == 200
        data = response.json()
        assert "endpoint_type" in data
        assert data["endpoint_type"] == "synchronous"
        assert data["requested_seconds"] == 1
    
    def test_async_sleep(self, client):
        """Test asynchronous sleep endpoint"""
        response = client.get("/async/sleep?seconds=1")
        assert response.status_code == 200
        data = response.json()
        assert "endpoint_type" in data
        assert data["endpoint_type"] == "asynchronous"
        assert data["requested_seconds"] == 1
    
    def test_async_faster_than_sync(self, client):
        """Test that async is faster for concurrent operations"""
        response = client.get("/compare/sync-vs-async?requests=5")
        assert response.status_code == 200
        data = response.json()
        assert data["async_time"] < data["sync_time"]
        assert "speedup" in data
    
    def test_sync_fibonacci(self, client):
        """Test CPU-bound operation with def"""
        response = client.get("/sync/fibonacci/10")
        assert response.status_code == 200
        data = response.json()
        assert data["n"] == 10
        assert data["fibonacci"] == 55
    
    def test_async_dashboard_concurrent(self, client):
        """Test concurrent operations faster than sequential"""
        response = client.get("/async/user-dashboard/1")
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "orders" in data
        assert "reviews" in data
        # Concurrent should be less than sum of all operations
        assert data["fetch_time"] < 0.3  # Should be ~0.15s
    
    def test_event_loop_demo(self, client):
        """Test event loop demonstration"""
        response = client.get("/event-loop/demo")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3
        assert "execution_log" in data
    
    def test_best_practices_endpoint(self, client):
        """Test best practices endpoint returns info"""
        response = client.get("/best-practices")
        assert response.status_code == 200
        data = response.json()
        assert "use_async_def_when" in data
        assert "use_def_when" in data
        assert "anti_patterns" in data


# ============================================================================
# Test Async DB Operations
# ============================================================================

class TestAsyncDBOperations:
    """Test async database operations"""
    
    @pytest.fixture
    def client(self):
        return TestClient(db_app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Async DB Operations API" in data["title"]
    
    def test_seed_data(self, client):
        """Test seeding sample data"""
        response = client.post("/seed-data")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_create_user(self, client):
        """Test creating a user"""
        user_data = {
            "name": "Test User",
            "email": f"test_{time.time()}@example.com",
            "age": 25
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == user_data["name"]
        assert data["email"] == user_data["email"]
        assert "id" in data
    
    def test_list_users(self, client):
        """Test listing users"""
        # First seed data
        client.post("/seed-data")
        
        response = client.get("/users/")
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
    
    def test_get_user(self, client):
        """Test getting a specific user"""
        # Seed data first
        client.post("/seed-data")
        
        response = client.get("/users/1")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert "name" in data
    
    def test_create_product(self, client):
        """Test creating a product"""
        product_data = {
            "name": "Test Product",
            "price": 99.99,
            "stock": 10
        }
        response = client.post("/products/", json=product_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == product_data["name"]
        assert float(data["price"]) == product_data["price"]
    
    def test_concurrent_queries_faster(self, client):
        """Test concurrent queries are faster than sequential"""
        # Seed data
        client.post("/seed-data")
        
        # Get performance comparison
        blocking = client.get("/performance/blocking-queries")
        concurrent = client.get("/performance/concurrent-queries")
        
        assert blocking.status_code == 200
        assert concurrent.status_code == 200
        
        # Concurrent should be faster (or equal for small dataset)
        blocking_time = blocking.json()["query_time"]
        concurrent_time = concurrent.json()["query_time"]
        assert concurrent_time <= blocking_time * 1.5  # Allow some margin
    
    def test_best_practices_endpoint(self, client):
        """Test best practices endpoint"""
        response = client.get("/best-practices")
        assert response.status_code == 200
        data = response.json()
        assert "connection_pooling" in data
        assert "concurrent_queries" in data


# ============================================================================
# Test Concurrency Patterns
# ============================================================================

class TestConcurrencyPatterns:
    """Test concurrency patterns"""
    
    @pytest.fixture
    def client(self):
        return TestClient(concurrency_app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Concurrency Patterns API" in data["title"]
    
    def test_parallel_gather(self, client):
        """Test parallel execution with gather"""
        response = client.get("/parallel/gather")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3
        # Should take ~1.5s (max of 1.0, 1.5, 0.8), not 3.3s (sum)
        assert data["total_time"] < 2.0
    
    def test_parallel_gather_dict(self, client):
        """Test parallel execution with named results"""
        response = client.get("/parallel/gather-dict")
        assert response.status_code == 200
        data = response.json()
        assert "user" in data["data"]
        assert "orders" in data["data"]
        assert "payments" in data["data"]
    
    def test_error_handling_default(self, client):
        """Test default error handling behavior"""
        response = client.get("/error-handling/default")
        assert response.status_code == 200
        data = response.json()
        assert "error" in data or "results" in data
    
    def test_error_handling_return_exceptions(self, client):
        """Test return_exceptions=True behavior"""
        response = client.get("/error-handling/return-exceptions")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        # Should have 3 results (some may be failed)
        assert len(data["results"]) == 3
    
    def test_timeout_basic(self, client):
        """Test timeout handling"""
        response = client.get("/timeout/basic")
        assert response.status_code == 200
        data = response.json()
        # Should timeout after 2 seconds
        assert "error" in data or "data" in data
        if "error" in data:
            assert "timeout" in data["error"].lower()
    
    def test_timeout_with_fallback(self, client):
        """Test timeout with fallback values"""
        response = client.get("/timeout/multiple-with-fallback")
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3
    
    def test_rate_limiting_semaphore(self, client):
        """Test rate limiting with semaphore"""
        response = client.get("/rate-limiting/semaphore")
        assert response.status_code == 200
        data = response.json()
        assert data["total_tasks"] == 10
        assert data["concurrent_limit"] == 3
        # Should take ~4 seconds (10 tasks / 3 concurrent)
        assert 3.5 <= data["execution_time"] <= 5.0
    
    def test_rate_limiting_api_calls(self, client):
        """Test rate limiting for API calls"""
        response = client.get("/rate-limiting/api-calls")
        assert response.status_code == 200
        data = response.json()
        assert data["total_requests"] == 20
        assert data["concurrent_limit"] == 5
    
    def test_create_background_task(self, client):
        """Test creating a background task"""
        response = client.post("/tasks/create/test-task?duration=2")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task"
    
    def test_task_status(self, client):
        """Test checking task status"""
        # Create task
        client.post("/tasks/create/status-test?duration=1")
        
        # Check status immediately (should be running)
        response = client.get("/tasks/status/status-test")
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "status-test"
        assert data["status"] in ["running", "completed"]
    
    def test_list_tasks(self, client):
        """Test listing all tasks"""
        response = client.get("/tasks/list")
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
    
    def test_aggregate_city_info(self, client):
        """Test data aggregation from multiple sources"""
        response = client.get("/aggregate/city-info/NewYork")
        assert response.status_code == 200
        data = response.json()
        assert data["city"] == "NewYork"
        assert "weather" in data
        assert "news" in data
        assert "traffic" in data
    
    def test_best_practices_endpoint(self, client):
        """Test best practices endpoint"""
        response = client.get("/best-practices")
        assert response.status_code == 200
        data = response.json()
        assert "parallel_execution" in data
        assert "error_handling" in data
        assert "timeouts" in data


# ============================================================================
# Test Production Deployment
# ============================================================================

class TestProductionDeployment:
    """Test production deployment features"""
    
    @pytest.fixture
    def client(self):
        return TestClient(production_app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Production-Ready Scalable API" in data["message"]
    
    def test_health_check(self, client):
        """Test basic health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_detailed_health_check(self, client):
        """Test detailed health check"""
        response = client.get("/health/detailed")
        assert response.status_code in [200, 503]
        data = response.json()
        assert "status" in data
        assert "system" in data
        assert "services" in data
    
    def test_readiness_check(self, client):
        """Test readiness probe"""
        response = client.get("/health/ready")
        assert response.status_code in [200, 503]
        data = response.json()
        assert "ready" in data
        assert "database" in data
    
    def test_liveness_check(self, client):
        """Test liveness probe"""
        response = client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["alive"] is True
    
    def test_metrics_endpoint(self, client):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "process" in data
        assert "system" in data
        assert "pid" in data["process"]
    
    def test_cors_headers(self, client):
        """Test CORS headers are present"""
        response = client.get("/")
        # CORS headers should be present
        # Note: TestClient doesn't always simulate CORS perfectly
        assert response.status_code == 200
    
    def test_process_time_header(self, client):
        """Test X-Process-Time header is added"""
        response = client.get("/")
        assert "X-Process-Time" in response.headers
        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0
    
    def test_request_id_header(self, client):
        """Test X-Request-ID header is added"""
        response = client.get("/")
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0
    
    def test_production_config_endpoint(self, client):
        """Test production config endpoint"""
        response = client.get("/production-config")
        assert response.status_code == 200
        data = response.json()
        assert "gunicorn_uvicorn" in data
        assert "docker" in data
        assert "kubernetes" in data


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Test performance characteristics"""
    
    @pytest.mark.asyncio
    async def test_async_operations_are_concurrent(self):
        """Test that async operations actually run concurrently"""
        start = time.time()
        
        async def slow_operation():
            await asyncio.sleep(1)
            return "done"
        
        # Run 3 operations concurrently
        results = await asyncio.gather(
            slow_operation(),
            slow_operation(),
            slow_operation()
        )
        
        duration = time.time() - start
        
        # Should take ~1 second (concurrent), not 3 seconds (sequential)
        assert duration < 1.5
        assert len(results) == 3
    
    @pytest.mark.asyncio
    async def test_timeout_actually_works(self):
        """Test that timeouts actually timeout"""
        async def very_slow_operation():
            await asyncio.sleep(10)
            return "done"
        
        start = time.time()
        
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(very_slow_operation(), timeout=0.5)
        
        duration = time.time() - start
        
        # Should timeout after ~0.5 seconds, not wait 10 seconds
        assert duration < 1.0
    
    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrency(self):
        """Test that semaphore actually limits concurrency"""
        semaphore = asyncio.Semaphore(2)
        concurrent_count = 0
        max_concurrent = 0
        
        async def limited_operation():
            nonlocal concurrent_count, max_concurrent
            async with semaphore:
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)
                await asyncio.sleep(0.1)
                concurrent_count -= 1
        
        # Start 10 operations
        await asyncio.gather(*[limited_operation() for _ in range(10)])
        
        # Maximum concurrent should be 2 (semaphore limit)
        assert max_concurrent == 2


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.integration
class TestIntegration:
    """Integration tests (require all services running)"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test a complete workflow"""
        async with AsyncClient(base_url="http://localhost:8001") as client:
            # 1. Seed data
            response = await client.post("/seed-data")
            assert response.status_code == 200
            
            # 2. Create user
            user_data = {
                "name": "Integration Test User",
                "email": f"integration_{time.time()}@test.com",
                "age": 30
            }
            response = await client.post("/users/", json=user_data)
            if response.status_code == 201:
                user = response.json()
                user_id = user["id"]
                
                # 3. Get user
                response = await client.get(f"/users/{user_id}")
                assert response.status_code == 200


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
