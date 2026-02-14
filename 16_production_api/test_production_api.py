"""
Tests for Production API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    """Setup and teardown test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Production REST API"

def test_health_check():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "redis" in data

def test_create_task():
    """Test creating a task"""
    response = client.post("/tasks", json={
        "title": "Test Task",
        "description": "Test Description",
        "priority": "high"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["priority"] == "high"
    assert "id" in data

def test_create_task_validation():
    """Test task creation validation"""
    # Empty title
    response = client.post("/tasks", json={
        "title": "",
        "description": "Test"
    })
    assert response.status_code == 422
    
    # Invalid priority
    response = client.post("/tasks", json={
        "title": "Test",
        "priority": "invalid"
    })
    assert response.status_code == 422

def test_list_tasks():
    """Test listing tasks"""
    # Create some tasks
    for i in range(3):
        client.post("/tasks", json={
            "title": f"Task {i}",
            "priority": "medium"
        })
    
    # List tasks
    response = client.get("/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

def test_list_tasks_with_filters():
    """Test filtering tasks"""
    # Create tasks with different priorities
    client.post("/tasks", json={"title": "High Priority", "priority": "high"})
    client.post("/tasks", json={"title": "Low Priority", "priority": "low"})
    
    # Filter by priority
    response = client.get("/tasks?priority=high")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["priority"] == "high"

def test_get_task():
    """Test getting a specific task"""
    # Create task
    create_response = client.post("/tasks", json={
        "title": "Test Task"
    })
    task_id = create_response.json()["id"]
    
    # Get task
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"

def test_get_nonexistent_task():
    """Test getting a task that doesn't exist"""
    response = client.get("/tasks/99999")
    assert response.status_code == 404

def test_update_task():
    """Test updating a task"""
    # Create task
    create_response = client.post("/tasks", json={
        "title": "Original Title",
        "priority": "low"
    })
    task_id = create_response.json()["id"]
    
    # Update task
    response = client.put(f"/tasks/{task_id}", json={
        "title": "Updated Title",
        "completed": True,
        "priority": "high"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["completed"] is True
    assert data["priority"] == "high"

def test_partial_update_task():
    """Test partial update of a task"""
    # Create task
    create_response = client.post("/tasks", json={
        "title": "Original Title",
        "description": "Original Description"
    })
    task_id = create_response.json()["id"]
    
    # Update only title
    response = client.put(f"/tasks/{task_id}", json={
        "title": "New Title"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["description"] == "Original Description"

def test_delete_task():
    """Test deleting a task"""
    # Create task
    create_response = client.post("/tasks", json={
        "title": "Task to Delete"
    })
    task_id = create_response.json()["id"]
    
    # Delete task
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_task():
    """Test deleting a task that doesn't exist"""
    response = client.delete("/tasks/99999")
    assert response.status_code == 404

def test_statistics():
    """Test statistics endpoint"""
    # Create tasks
    client.post("/tasks", json={"title": "Task 1", "priority": "high"})
    client.post("/tasks", json={"title": "Task 2", "priority": "low"})
    client.post("/tasks", json={"title": "Task 3", "priority": "medium"})
    
    # Mark one as completed
    create_response = client.post("/tasks", json={"title": "Task 4"})
    task_id = create_response.json()["id"]
    client.put(f"/tasks/{task_id}", json={"completed": True})
    
    # Get statistics
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 4
    assert data["completed"] == 1
    assert data["pending"] == 3
    assert "by_priority" in data
    assert "completion_rate" in data

def test_pagination():
    """Test pagination"""
    # Create 15 tasks
    for i in range(15):
        client.post("/tasks", json={"title": f"Task {i}"})
    
    # Get first page
    response = client.get("/tasks?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    
    # Get second page
    response = client.get("/tasks?skip=10&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
