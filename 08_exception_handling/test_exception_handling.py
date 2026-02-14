"""
Test Suite for FastAPI Exception Handling
========================================

Tests for both basic and custom exception handling.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime


# ============================================================================
# Tests for Basic Exception Handling
# ============================================================================

def test_basic_api():
    """Test basic exception handling API"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    response = client.get("/")
    assert response.status_code == 200
    assert "Exception Handling API" in response.json()["message"]


def test_get_item_found():
    """Test getting an existing item"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["name"] == "Laptop"


def test_get_item_not_found():
    """Test HTTPException for item not found"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    response = client.get("/items/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_create_item_valid():
    """Test creating a valid item"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    item_data = {
        "name": "New Item",
        "price": 99.99,
        "quantity": 10,
        "description": "Test item"
    }
    
    response = client.post("/items", json=item_data)
    assert response.status_code == 201
    assert response.json()["name"] == "New Item"
    assert "id" in response.json()


def test_create_item_invalid_price():
    """Test validation error for invalid price"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    item_data = {
        "name": "Invalid Item",
        "price": -10,  # Invalid: must be positive
        "quantity": 5
    }
    
    response = client.post("/items", json=item_data)
    assert response.status_code == 422  # Validation error


def test_create_item_invalid_quantity():
    """Test validation error for negative quantity"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    item_data = {
        "name": "Invalid Item",
        "price": 10.0,
        "quantity": -5  # Invalid: cannot be negative
    }
    
    response = client.post("/items", json=item_data)
    assert response.status_code == 422


def test_create_item_special_chars():
    """Test validation error for special characters in name"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    item_data = {
        "name": "Item<script>",  # Invalid: contains special chars
        "price": 10.0,
        "quantity": 5
    }
    
    response = client.post("/items", json=item_data)
    assert response.status_code == 422


def test_update_item_success():
    """Test updating an existing item"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    item_data = {
        "name": "Updated Laptop",
        "price": 1099.99,
        "quantity": 8
    }
    
    response = client.put("/items/1", json=item_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Laptop"
    assert response.json()["price"] == 1099.99


def test_update_item_not_found():
    """Test updating non-existent item"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    item_data = {
        "name": "Non-existent",
        "price": 99.99,
        "quantity": 5
    }
    
    response = client.put("/items/999", json=item_data)
    assert response.status_code == 404


def test_delete_item_with_quantity():
    """Test that items with quantity cannot be deleted"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    response = client.delete("/items/1")
    assert response.status_code == 400
    assert "quantity" in response.json()["detail"].lower()


def test_protected_endpoint_no_key():
    """Test protected endpoint without API key"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    response = client.get("/protected")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


def test_protected_endpoint_invalid_key():
    """Test protected endpoint with invalid API key"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    response = client.get("/protected", headers={"X-API-Key": "invalid"})
    assert response.status_code == 403


def test_protected_endpoint_valid_key():
    """Test protected endpoint with valid API key"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    response = client.get("/protected", headers={"X-API-Key": "secret-key-123"})
    assert response.status_code == 200
    assert response.json()["message"] == "Access granted"


def test_divide_numbers_success():
    """Test successful division"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    response = client.get("/divide/10/2")
    assert response.status_code == 200
    assert response.json()["result"] == 5.0


def test_divide_by_zero():
    """Test division by zero error"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    response = client.get("/divide/10/0")
    assert response.status_code == 400
    assert "division by zero" in response.json()["detail"].lower()


def test_list_items_pagination():
    """Test listing items with pagination"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    response = client.get("/items?skip=0&limit=2")
    assert response.status_code == 200
    assert response.json()["skip"] == 0
    assert response.json()["limit"] == 2


def test_list_items_invalid_skip():
    """Test validation error for negative skip"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    response = client.get("/items?skip=-1")
    assert response.status_code == 422


def test_list_items_invalid_limit():
    """Test validation error for limit exceeding max"""
    from exception_handling import app_basic
    client = TestClient(app_basic.app)
    
    response = client.get("/items?limit=101")
    assert response.status_code == 422


# ============================================================================
# Tests for Custom Exception Handling
# ============================================================================

def test_custom_api():
    """Test custom exception handling API"""
    from exception_handling import app_custom
    client = TestClient(app_custom.app)
    
    response = client.get("/")
    assert response.status_code == 200
    assert "Custom Exception Handling API" in response.json()["message"]


def test_custom_get_item_not_found():
    """Test custom ItemNotFoundError"""
    from exception_handling import app_custom
    client = TestClient(app_custom.app)
    
    response = client.get("/items/999")
    assert response.status_code == 404
    assert response.json()["error"] == "ItemNotFound"
    assert response.json()["item_id"] == 999
    assert "timestamp" in response.json()
    assert "path" in response.json()


def test_custom_create_item_success():
    """Test creating item with custom exception handling"""
    from exception_handling import app_custom
    client = TestClient(app_custom.app)
    
    item_data = {
        "name": "Test Item",
        "price": 49.99,
        "quantity": 20,
        "category": "electronics"
    }
    
    response = client.post("/items", json=item_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Item"


def test_custom_create_duplicate_item():
    """Test ItemAlreadyExistsError for duplicate"""
    from exception_handling import app_custom
    client = TestClient(app_custom.app)
    
    item_data = {
        "name": "Laptop",  # Already exists
        "price": 999.99,
        "quantity": 5,
        "category": "electronics"
    }
    
    response = client.post("/items", json=item_data)
    assert response.status_code == 409
    assert response.json()["error"] == "ItemAlreadyExists"
    assert "Laptop" in response.json()["item_name"]


def test_custom_create_invalid_category():
    """Test ValueError for invalid category"""
    from exception_handling import app_custom
    client = TestClient(app_custom.app)
    
    item_data = {
        "name": "New Item",
        "price": 99.99,
        "quantity": 10,
        "category": "invalid_category"
    }
    
    response = client.post("/items", json=item_data)
    assert response.status_code == 422


def test_custom_place_order_success():
    """Test successful order placement"""
    from exception_handling import app_custom
    client = TestClient(app_custom.app)
    
    order_data = {
        "item_id": 1,
        "quantity": 2
    }
    
    response = client.post("/orders", json=order_data)
    assert response.status_code == 201
    assert "order_id" in response.json()
    assert response.json()["quantity"] == 2


def test_custom_place_order_item_not_found():
    """Test order with non-existent item"""
    from exception_handling import app_custom
    client = TestClient(app_custom.app)
    
    order_data = {
        "item_id": 999,
        "quantity": 1
    }
    
    response = client.post("/orders", json=order_data)
    assert response.status_code == 404
    assert response.json()["error"] == "ItemNotFound"


def test_custom_place_order_insufficient_stock():
    """Test InsufficientStockError"""
    from exception_handling import app_custom
    client = TestClient(app_custom.app)
    
    order_data = {
        "item_id": 1,
        "quantity": 9999  # More than available
    }
    
    response = client.post("/orders", json=order_data)
    assert response.status_code == 400
    assert response.json()["error"] == "InsufficientStock"
    assert response.json()["requested"] == 9999
    assert "available" in response.json()


def test_custom_delete_item_with_stock():
    """Test InvalidOperationError for deleting item with stock"""
    from exception_handling import app_custom
    client = TestClient(app_custom.app)
    
    response = client.delete("/items/1")
    assert response.status_code == 422
    assert response.json()["error"] == "INVALID_OPERATION"
    assert "stock" in response.json()["message"].lower()


def test_custom_validation_error_format():
    """Test custom validation error format"""
    from exception_handling import app_custom
    client = TestClient(app_custom.app)
    
    # Send invalid data
    response = client.post("/items", json={
        "name": "",  # Too short
        "price": -10,  # Invalid
        "quantity": -5,  # Invalid
        "category": "electronics"
    })
    
    assert response.status_code == 422
    assert response.json()["error"] == "ValidationError"
    assert "details" in response.json()
    assert isinstance(response.json()["details"], list)


def test_custom_trigger_unexpected_error():
    """Test catch-all exception handler"""
    from exception_handling import app_custom
    client = TestClient(app_custom.app)
    
    response = client.get("/test-error")
    assert response.status_code == 500
    assert response.json()["error"] == "InternalServerError"
    assert "unexpected" in response.json()["message"].lower()


def test_custom_trigger_value_error():
    """Test ValueError handler"""
    from exception_handling import app_custom
    client = TestClient(app_custom.app)
    
    response = client.get("/test-value-error")
    assert response.status_code == 400
    assert response.json()["error"] == "ValueError"


def test_custom_list_items():
    """Test listing items"""
    from exception_handling import app_custom
    client = TestClient(app_custom.app)
    
    response = client.get("/items")
    assert response.status_code == 200
    assert "items" in response.json()
    assert isinstance(response.json()["items"], list)


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
