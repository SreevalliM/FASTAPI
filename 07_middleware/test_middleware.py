"""
Test suite for middleware examples.

Run with: pytest test_middleware.py -v
"""

import pytest
from fastapi.testclient import TestClient
import time
import importlib.util
import sys
from pathlib import Path

# Helper function to import modules with numeric prefixes
def import_module_from_file(module_name: str, file_path: str):
    """Import a module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Get the current directory
current_dir = Path(__file__).parent

# Import all the middleware modules
middleware_basic = import_module_from_file(
    "middleware_basic",
    str(current_dir / "07_middleware_basic.py")
)
logging_middleware = import_module_from_file(
    "logging_middleware",
    str(current_dir / "07_logging_middleware.py")
)
timing_middleware = import_module_from_file(
    "timing_middleware",
    str(current_dir / "07_timing_middleware.py")
)
cors_middleware = import_module_from_file(
    "cors_middleware",
    str(current_dir / "07_cors_middleware.py")
)


# ============================================================================
# Test Basic Middleware
# ============================================================================

def test_basic_middleware_logging():
    """Test that basic middleware adds process time header."""
    client = TestClient(middleware_basic.app)
    response = client.get("/")
    
    assert response.status_code == 200
    assert "X-Process-Time" in response.headers
    assert float(response.headers["X-Process-Time"]) >= 0


def test_basic_middleware_fast_endpoint():
    """Test fast endpoint has low process time."""
    client = TestClient(middleware_basic.app)
    response = client.get("/fast")
    
    assert response.status_code == 200
    process_time = float(response.headers.get("X-Process-Time", "0"))
    assert process_time < 1.0  # Should be fast


def test_basic_middleware_slow_endpoint():
    """Test slow endpoint has expected process time."""
    client = TestClient(middleware_basic.app)
    response = client.get("/slow")
    
    assert response.status_code == 200
    process_time = float(response.headers.get("X-Process-Time", "0"))
    assert process_time >= 2.0  # Should take at least 2 seconds


def test_basic_middleware_cors_headers():
    """Test that CORS headers are present."""
    client = TestClient(middleware_basic.app)
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )
    
    assert "access-control-allow-origin" in response.headers


# ============================================================================
# Test Logging Middleware
# ============================================================================

def test_logging_middleware_request_id():
    """Test that request ID is added to response."""
    client = TestClient(logging_middleware.app)
    response = client.get("/")
    
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    
    # Request ID should be a valid UUID
    request_id = response.headers["X-Request-ID"]
    assert len(request_id) > 0
    assert "-" in request_id  # UUIDs contain dashes


def test_logging_middleware_multiple_requests_unique_ids():
    """Test that each request gets a unique ID."""
    client = TestClient(logging_middleware.app)
    response1 = client.get("/")
    response2 = client.get("/")
    
    id1 = response1.headers["X-Request-ID"]
    id2 = response2.headers["X-Request-ID"]
    
    assert id1 != id2  # Each request should have unique ID


def test_logging_middleware_error_handling():
    """Test that errors are properly logged and handled."""
    client = TestClient(logging_middleware.app)
    response = client.get("/error")
    
    assert response.status_code == 500
    assert "request_id" in response.json()


def test_logging_middleware_login_endpoint():
    """Test login endpoint (sensitive data filtering)."""
    client = TestClient(logging_middleware.app)
    response = client.post(
        "/login",
        json={"username": "testuser", "password": "secret"}
    )
    
    assert response.status_code == 200
    assert "request_id" in response.json()


# ============================================================================
# Test Timing Middleware
# ============================================================================

def test_timing_middleware_headers():
    """Test that timing headers are present."""
    client = TestClient(timing_middleware.app)
    response = client.get("/")
    
    assert response.status_code == 200
    assert "X-Process-Time" in response.headers
    assert "X-Total-Time" in response.headers
    assert "X-Performance" in response.headers


def test_timing_middleware_performance_classification():
    """Test performance classification."""
    client = TestClient(timing_middleware.app)
    
    # Fast endpoint should be "excellent"
    response = client.get("/fast")
    assert response.headers["X-Performance"] == "excellent"
    
    # Slow endpoint should be "slow" or "very-slow"
    response = client.get("/slow")
    performance = response.headers["X-Performance"]
    assert performance in ["slow", "very-slow"]


def test_timing_middleware_statistics():
    """Test statistics collection."""
    client = TestClient(timing_middleware.app)
    
    # Make some requests
    client.get("/fast")
    client.get("/fast")
    client.get("/medium")
    
    # Get statistics
    response = client.get("/statistics")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_requests" in data
    assert data["total_requests"] >= 3


def test_timing_middleware_reset_statistics():
    """Test statistics reset."""
    client = TestClient(timing_middleware.app)
    
    # Make some requests
    client.get("/fast")
    
    # Reset statistics
    response = client.post("/reset-statistics")
    assert response.status_code == 200
    
    # Verify reset
    response = client.get("/statistics")
    data = response.json()
    # After reset, should have just the /statistics and /reset-statistics calls
    assert data["total_requests"] <= 2


def test_timing_middleware_process_time_format():
    """Test that process time is a valid number."""
    client = TestClient(timing_middleware.app)
    response = client.get("/")
    
    process_time = response.headers["X-Process-Time"]
    # Should be a valid float
    assert float(process_time) >= 0


# ============================================================================
# Test CORS Middleware
# ============================================================================

def test_cors_basic_configuration():
    """Test basic CORS configuration."""
    client = TestClient(cors_middleware.app)
    response = client.get("/")
    
    assert response.status_code == 200


def test_cors_preflight_request():
    """Test CORS preflight request."""
    client = TestClient(cors_middleware.app)
    
    # Simulate preflight request
    response = client.options(
        "/preflight/complex",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"
        }
    )
    
    # Check CORS headers
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers


def test_cors_simple_get_request():
    """Test simple GET request with CORS."""
    client = TestClient(cors_middleware.app)
    response = client.get(
        "/preflight/simple",
        headers={"Origin": "http://localhost:3000"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "simple_request"


def test_cors_post_request():
    """Test POST request with CORS."""
    client = TestClient(cors_middleware.app)
    response = client.post(
        "/preflight/complex",
        json={"test": "data"},
        headers={"Origin": "http://localhost:3000"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "complex_request"
    assert data["received"]["test"] == "data"


def test_cors_custom_header():
    """Test custom header exposure."""
    client = TestClient(cors_middleware.app)
    response = client.get(
        "/preflight/with-custom-header",
        headers={"Origin": "http://localhost:3000"}
    )
    
    assert response.status_code == 200
    assert "X-Custom-Header" in response.headers


# ============================================================================
# Integration Tests
# ============================================================================

def test_multiple_middleware_interaction():
    """Test that multiple middleware work together correctly."""
    client = TestClient(logging_middleware.app)
    response = client.get("/test/123")
    
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    
    data = response.json()
    assert data["item_id"] == 123
    assert "request_id" in data


def test_middleware_order_request_state():
    """Test that middleware can share data via request.state."""
    client = TestClient(logging_middleware.app)
    response = client.get("/")
    
    data = response.json()
    # Request ID should be available in endpoint via request.state
    assert "request_id" in data


# ============================================================================
# Performance Tests
# ============================================================================

def test_middleware_overhead():
    """Test that middleware overhead is minimal."""
    client = TestClient(middleware_basic.app)
    
    # Measure multiple requests
    times = []
    for _ in range(10):
        response = client.get("/fast")
        process_time = float(response.headers.get("X-Process-Time", "0"))
        times.append(process_time)
    
    # Average overhead should be minimal (< 0.1s)
    avg_time = sum(times) / len(times)
    assert avg_time < 0.1


def test_concurrent_requests():
    """Test that middleware handles concurrent requests correctly."""
    client = TestClient(logging_middleware.app)
    
    # Make multiple requests
    responses = []
    for _ in range(5):
        response = client.get("/")
        responses.append(response)
    
    # All should succeed
    for response in responses:
        assert response.status_code == 200
    
    # All should have unique request IDs
    request_ids = [r.headers["X-Request-ID"] for r in responses]
    assert len(request_ids) == len(set(request_ids))  # All unique


# ============================================================================
# Edge Cases
# ============================================================================

def test_large_response_with_middleware():
    """Test middleware with large responses."""
    client = TestClient(middleware_basic.app)
    response = client.get("/large-response")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1000


def test_post_with_body():
    """Test middleware with POST request body."""
    client = TestClient(middleware_basic.app)
    test_data = {"key": "value", "number": 42}
    response = client.post("/data", json=test_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["received"] == test_data


def test_http_error_with_middleware():
    """Test that HTTP errors pass through middleware correctly."""
    client = TestClient(logging_middleware.app)
    response = client.get("/http-error")
    
    assert response.status_code == 404


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def basic_client():
    """Fixture for basic middleware client."""
    return TestClient(middleware_basic.app)


@pytest.fixture
def logging_client():
    """Fixture for logging middleware client."""
    return TestClient(logging_middleware.app)


@pytest.fixture
def timing_client():
    """Fixture for timing middleware client."""
    return TestClient(timing_middleware.app)


@pytest.fixture
def cors_client():
    """Fixture for CORS middleware client."""
    return TestClient(cors_middleware.app)


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
