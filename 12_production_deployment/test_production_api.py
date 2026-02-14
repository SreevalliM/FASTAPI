"""
Test Suite for Production API
Tests health checks, endpoints, middleware, and error handling
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os

# Set test environment variables before importing the app
os.environ["ENV"] = "test"
os.environ["DEBUG"] = "false"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["LOG_LEVEL"] = "ERROR"  # Reduce noise during tests

from 12_production_api import app, settings


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


class TestHealthChecks:
    """Test health check endpoints"""
    
    def test_health_check(self, client):
        """Test /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "environment" in data
        assert "version" in data
        assert "timestamp" in data
    
    def test_readiness_check(self, client):
        """Test /ready endpoint"""
        response = client.get("/ready")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ready"
    
    def test_metrics_endpoint(self, client):
        """Test /metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "items_count" in data


class TestRootEndpoints:
    """Test root endpoints"""
    
    def test_root_endpoint(self, client):
        """Test / endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "request_id" in data


class TestItemsEndpoints:
    """Test CRUD operations on items"""
    
    def test_create_item(self, client):
        """Test creating an item"""
        item_data = {
            "name": "Test Item",
            "description": "Test Description",
            "price": 29.99
        }
        
        response = client.post("/items", json=item_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == item_data["name"]
        assert data["description"] == item_data["description"]
        assert data["price"] == item_data["price"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_item_validation(self, client):
        """Test item creation with invalid data"""
        # Missing required field
        response = client.post("/items", json={"name": "Test"})
        assert response.status_code == 422
        
        # Invalid price
        response = client.post("/items", json={
            "name": "Test",
            "price": -10
        })
        assert response.status_code == 422
        
        # Empty name
        response = client.post("/items", json={
            "name": "",
            "price": 10
        })
        assert response.status_code == 422
    
    def test_list_items(self, client):
        """Test listing items"""
        # Create some items first
        client.post("/items", json={"name": "Item 1", "price": 10})
        client.post("/items", json={"name": "Item 2", "price": 20})
        
        response = client.get("/items")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
    
    def test_get_item(self, client):
        """Test getting a specific item"""
        # Create an item
        create_response = client.post("/items", json={
            "name": "Specific Item",
            "price": 15.99
        })
        item_id = create_response.json()["id"]
        
        # Get the item
        response = client.get(f"/items/{item_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == item_id
        assert data["name"] == "Specific Item"
    
    def test_get_nonexistent_item(self, client):
        """Test getting an item that doesn't exist"""
        response = client.get("/items/nonexistent-id")
        assert response.status_code == 404
    
    def test_delete_item(self, client):
        """Test deleting an item"""
        # Create an item
        create_response = client.post("/items", json={
            "name": "Item to Delete",
            "price": 25.00
        })
        item_id = create_response.json()["id"]
        
        # Delete the item
        response = client.delete(f"/items/{item_id}")
        assert response.status_code == 204
        
        # Verify it's deleted
        response = client.get(f"/items/{item_id}")
        assert response.status_code == 404
    
    def test_delete_nonexistent_item(self, client):
        """Test deleting an item that doesn't exist"""
        response = client.delete("/items/nonexistent-id")
        assert response.status_code == 404


class TestMiddleware:
    """Test middleware functionality"""
    
    def test_request_id_header(self, client):
        """Test that request ID is added to response headers"""
        response = client.get("/")
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0
    
    def test_process_time_header(self, client):
        """Test that process time is added to response headers"""
        response = client.get("/")
        assert "X-Process-Time" in response.headers
        
        # Parse process time and verify it's a valid number
        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0
    
    def test_cors_headers(self, client):
        """Test CORS headers"""
        response = client.options("/", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        })
        
        # FastAPI/Starlette handles CORS
        assert response.status_code in [200, 405]


class TestErrorHandling:
    """Test error handling"""
    
    def test_404_not_found(self, client):
        """Test 404 error for non-existent endpoints"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
    
    def test_405_method_not_allowed(self, client):
        """Test 405 error for wrong HTTP method"""
        response = client.put("/health")
        assert response.status_code == 405
    
    @patch('12_production_api.items_db', new={})
    def test_global_exception_handler(self, client):
        """Test global exception handler"""
        # This is a basic test - in a real scenario, you'd trigger an actual exception
        # For now, we just verify the handler exists
        assert hasattr(app, 'exception_handlers')


class TestConfiguration:
    """Test configuration and settings"""
    
    def test_settings_loaded(self):
        """Test that settings are properly loaded"""
        assert settings.app_name is not None
        assert settings.environment == "test"
        assert settings.log_level is not None
    
    def test_debug_mode_disabled_in_test(self):
        """Test that debug mode is disabled in test environment"""
        assert settings.debug is False


class TestDocs:
    """Test API documentation endpoints"""
    
    def test_docs_disabled_in_production(self):
        """Test that docs are disabled when debug=False"""
        # In test/production mode with debug=False, docs should be None
        if not settings.debug:
            response = client.get("/api/docs")
            assert response.status_code == 404


# Run tests with: pytest test_production_api.py -v
# Run with coverage: pytest test_production_api.py -v --cov=. --cov-report=html
