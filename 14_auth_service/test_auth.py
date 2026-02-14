"""
Tests for Auth Service
"""
import pytest
from fastapi.testclient import TestClient
from main import app, users_db, refresh_tokens_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    """Reset databases before each test"""
    users_db.clear()
    refresh_tokens_db.clear()
    yield

def test_register_user():
    """Test user registration"""
    response = client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "role": "user"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["role"] == "user"
    assert "password" not in data

def test_register_duplicate_user():
    """Test registering duplicate username"""
    # Register first user
    client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    
    # Try to register again
    response = client.post("/register", json={
        "username": "testuser",
        "email": "test2@example.com",
        "password": "testpass456"
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_login_success():
    """Test successful login"""
    # Register user
    client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    
    # Login
    response = client.post("/token", data={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password():
    """Test login with wrong password"""
    # Register user
    client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    
    # Try to login with wrong password
    response = client.post("/token", data={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_access_protected_route():
    """Test accessing protected route with valid token"""
    # Register and login
    client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    
    login_response = client.post("/token", data={
        "username": "testuser",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]
    
    # Access protected route
    response = client.get("/protected", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"] == "testuser"
    assert data["role"] == "user"

def test_access_protected_without_token():
    """Test accessing protected route without token"""
    response = client.get("/protected")
    assert response.status_code == 401

def test_get_current_user():
    """Test getting current user info"""
    # Register and login
    client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    
    login_response = client.post("/token", data={
        "username": "testuser",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]
    
    # Get user info
    response = client.get("/users/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_refresh_token():
    """Test refreshing access token"""
    # Register and login
    client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    
    login_response = client.post("/token", data={
        "username": "testuser",
        "password": "testpass123"
    })
    refresh_token = login_response.json()["refresh_token"]
    
    # Refresh token
    response = client.post("/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != refresh_token  # New refresh token

def test_refresh_with_invalid_token():
    """Test refreshing with invalid token"""
    response = client.post("/refresh", json={
        "refresh_token": "invalid_token"
    })
    assert response.status_code == 401

def test_logout():
    """Test logout"""
    # Register and login
    client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    
    login_response = client.post("/token", data={
        "username": "testuser",
        "password": "testpass123"
    })
    access_token = login_response.json()["access_token"]
    refresh_token = login_response.json()["refresh_token"]
    
    # Logout
    response = client.post("/logout", 
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    
    # Try to use refresh token after logout
    response = client.post("/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 401

def test_rbac_admin_access():
    """Test RBAC: Admin can access admin routes"""
    # Register admin user
    client.post("/register", json={
        "username": "admin",
        "email": "admin@example.com",
        "password": "adminpass",
        "role": "admin"
    })
    
    login_response = client.post("/token", data={
        "username": "admin",
        "password": "adminpass"
    })
    token = login_response.json()["access_token"]
    
    # Access admin route
    response = client.get("/admin/users", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200

def test_rbac_user_cannot_access_admin():
    """Test RBAC: Regular user cannot access admin routes"""
    # Register regular user
    client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    
    login_response = client.post("/token", data={
        "username": "testuser",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]
    
    # Try to access admin route
    response = client.get("/admin/users", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]

def test_rbac_manager_access():
    """Test RBAC: Manager can access manager routes"""
    # Register manager user
    client.post("/register", json={
        "username": "manager",
        "email": "manager@example.com",
        "password": "managerpass",
        "role": "manager"
    })
    
    login_response = client.post("/token", data={
        "username": "manager",
        "password": "managerpass"
    })
    token = login_response.json()["access_token"]
    
    # Access manager route
    response = client.get("/manager/dashboard", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200

def test_admin_delete_user():
    """Test admin can delete users"""
    # Register admin and regular user
    client.post("/register", json={
        "username": "admin",
        "email": "admin@example.com",
        "password": "adminpass",
        "role": "admin"
    })
    
    client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    
    # Login as admin
    login_response = client.post("/token", data={
        "username": "admin",
        "password": "adminpass"
    })
    token = login_response.json()["access_token"]
    
    # Delete user
    response = client.delete("/admin/users/testuser", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]
