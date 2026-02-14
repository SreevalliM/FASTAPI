"""
Test Background Tasks
=====================

Testing background tasks in FastAPI
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import asyncio

# Import the app from basic example
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from 06_background_tasks_basic import app, task_logs
except ImportError:
    # Fallback for different import methods
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "background_tasks_basic",
        os.path.join(os.path.dirname(__file__), "06_background_tasks_basic.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    app = module.app
    task_logs = module.task_logs

client = TestClient(app)

# ========================================
# Test Setup
# ========================================

@pytest.fixture(autouse=True)
def clear_logs():
    """Clear logs before each test"""
    task_logs.clear()
    yield
    task_logs.clear()

# ========================================
# Test Basic Endpoints
# ========================================

def test_simple_notification():
    """Test simple notification endpoint"""
    response = client.post(
        "/simple/notification",
        json={
            "email": "test@example.com",
            "message": "Test message"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Notification queued successfully"
    assert data["email"] == "test@example.com"
    assert data["status"] == "processing"

def test_simple_notification_async():
    """Test async notification endpoint"""
    response = client.post(
        "/simple/notification-async",
        json={
            "email": "test@example.com",
            "message": "Test message"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Async notification queued successfully"

def test_create_order():
    """Test order creation with multiple background tasks"""
    response = client.post(
        "/order",
        json={
            "item": "Laptop",
            "quantity": 2,
            "email": "customer@example.com"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Order created successfully"
    assert data["order"]["item"] == "Laptop"
    assert data["order"]["quantity"] == 2

def test_create_order_async():
    """Test async order creation"""
    response = client.post(
        "/order-async",
        json={
            "item": "Phone",
            "quantity": 1,
            "email": "buyer@example.com"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processing"

# ========================================
# Test Background Task Execution
# ========================================

def test_background_task_executes():
    """Test that background task actually executes"""
    # Send request
    response = client.post(
        "/simple/notification",
        json={
            "email": "test@example.com",
            "message": "Test"
        }
    )
    
    assert response.status_code == 200
    
    # Wait for background task to complete
    import time
    time.sleep(4)  # Wait for 3-second task + buffer
    
    # Check that task ran (it should have added to logs)
    assert len(task_logs) > 0
    
    # Verify log content
    log_entry = task_logs[-1]
    assert "test@example.com" in log_entry

def test_multiple_background_tasks_execute():
    """Test that multiple background tasks execute in order"""
    response = client.post(
        "/order",
        json={
            "item": "Book",
            "quantity": 3,
            "email": "reader@example.com"
        }
    )
    
    assert response.status_code == 200
    
    # Wait for all tasks (3 tasks, ~2 seconds each)
    import time
    time.sleep(8)
    
    # Should have 3 log entries (one per task)
    assert len(task_logs) >= 3

# ========================================
# Test Logs Endpoint
# ========================================

def test_get_logs_empty():
    """Test getting logs when empty"""
    response = client.get("/logs")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_logs"] == 0
    assert data["logs"] == []

def test_get_logs_with_data():
    """Test getting logs with data"""
    # Add some logs manually for testing
    task_logs.append("[2024-01-01] Test log 1")
    task_logs.append("[2024-01-01] Test log 2")
    
    response = client.get("/logs")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_logs"] == 2
    assert len(data["logs"]) == 2

def test_clear_logs():
    """Test clearing logs"""
    # Add some logs
    task_logs.append("Test log")
    assert len(task_logs) == 1
    
    # Clear logs
    response = client.delete("/logs")
    
    assert response.status_code == 200
    assert len(task_logs) == 0

# ========================================
# Test Input Validation
# ========================================

def test_invalid_email():
    """Test invalid email format"""
    response = client.post(
        "/simple/notification",
        json={
            "email": "invalid-email",
            "message": "Test"
        }
    )
    
    assert response.status_code == 422  # Validation error

def test_missing_fields():
    """Test missing required fields"""
    response = client.post(
        "/simple/notification",
        json={"email": "test@example.com"}
    )
    
    assert response.status_code == 422

# ========================================
# Test Root Endpoint
# ========================================

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data

# ========================================
# Mock Testing Background Tasks
# ========================================

def test_background_task_with_mock():
    """Test background task with mocking"""
    with patch('background_tasks_basic.send_notification') as mock_send:
        response = client.post(
            "/simple/notification",
            json={
                "email": "test@example.com",
                "message": "Test"
            }
        )
        
        assert response.status_code == 200
        
        # Note: TestClient runs background tasks immediately
        # So we can check if the mock was called
        # (Behavior may vary based on FastAPI/Starlette version)

# ========================================
# Test Background Task Functions Directly
# ========================================

def test_send_notification_function():
    """Test send_notification function directly"""
    from background_tasks_basic import send_notification
    
    # Clear logs
    task_logs.clear()
    
    # Call function directly
    send_notification("test@example.com", "Test message")
    
    # Check logs were updated
    assert len(task_logs) > 0
    log_entry = task_logs[-1]
    assert "test@example.com" in log_entry
    assert "Test message" in log_entry

def test_process_order_function():
    """Test process_order function directly"""
    from background_tasks_basic import process_order
    
    task_logs.clear()
    
    process_order("Laptop", 2)
    
    assert len(task_logs) > 0
    log_entry = task_logs[-1]
    assert "2x Laptop" in log_entry

# ========================================
# Async Test Examples
# ========================================

@pytest.mark.asyncio
async def test_async_notification_function():
    """Test async notification function directly"""
    from background_tasks_basic import async_send_notification
    
    task_logs.clear()
    
    await async_send_notification("test@example.com", "Async test")
    
    assert len(task_logs) > 0
    log_entry = task_logs[-1]
    assert "ASYNC" in log_entry
    assert "test@example.com" in log_entry

# ========================================
# Performance Tests
# ========================================

def test_response_time_with_background_task():
    """Test that response is fast even with background tasks"""
    import time
    
    start = time.time()
    response = client.post(
        "/simple/notification",
        json={
            "email": "test@example.com",
            "message": "Test"
        }
    )
    duration = time.time() - start
    
    assert response.status_code == 200
    # Response should be fast (< 1 second)
    # Background task takes 3 seconds but doesn't block response
    assert duration < 1.0

# ========================================
# Integration Tests
# ========================================

def test_full_order_workflow():
    """Test complete order workflow"""
    # Create order
    response = client.post(
        "/order",
        json={
            "item": "Gaming Console",
            "quantity": 1,
            "email": "gamer@example.com"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "message" in data
    assert "order" in data
    assert "status" in data
    assert data["status"] == "processing"
    
    # Wait for background tasks
    import time
    time.sleep(8)
    
    # Verify tasks executed
    logs = client.get("/logs").json()
    assert logs["total_logs"] >= 3

# ========================================
# Run Tests
# ========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
