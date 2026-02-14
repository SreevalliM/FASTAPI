"""
🧪 Test OAuth2 + JWT Authentication
====================================
Tests for authentication, authorization, and protected endpoints.

Run tests:
    pytest test_authentication.py -v

Run with coverage:
    pytest test_authentication.py -v --cov

Note: To import the API module, run:
    python -c "import sys; sys.path.insert(0, '.'); import importlib; mod = importlib.import_module('05_user_auth_api')"
    
Or rename the file temporarily for testing.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import timedelta
from jose import jwt
import importlib.util
import sys

# Import module with number prefix (Python workaround)
spec = importlib.util.spec_from_file_location("user_auth_api", "05_user_auth_api.py")
auth_module = importlib.util.module_from_spec(spec)
sys.modules["user_auth_api"] = auth_module
spec.loader.exec_module(auth_module)

# Import from the loaded module
app = auth_module.app
get_password_hash = auth_module.get_password_hash
verify_password = auth_module.verify_password
create_access_token = auth_module.create_access_token
SECRET_KEY = auth_module.SECRET_KEY
ALGORITHM = auth_module.ALGORITHM
fake_users_db = auth_module.fake_users_db

# ==================== Test Setup ====================

client = TestClient(app)

@pytest.fixture
def alice_token():
    """Get valid token for alice (admin)"""
    response = client.post(
        "/token",
        data={"username": "alice", "password": "secret"}
    )
    return response.json()["access_token"]

@pytest.fixture
def bob_token():
    """Get valid token for bob (regular user)"""
    response = client.post(
        "/token",
        data={"username": "bob", "password": "secret"}
    )
    return response.json()["access_token"]

# ==================== Password Hashing Tests ====================

def test_password_hashing():
    """Test password hashing and verification"""
    password = "MySecurePassword123"
    hashed = get_password_hash(password)
    
    # Hash should be different from original
    assert hashed != password
    
    # Verification should work
    assert verify_password(password, hashed) is True
    
    # Wrong password should fail
    assert verify_password("WrongPassword", hashed) is False

def test_same_password_different_hashes():
    """Test that same password generates different hashes (salted)"""
    password = "test123"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # Hashes should be different (due to salt)
    assert hash1 != hash2
    
    # But both should verify correctly
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True

# ==================== JWT Token Tests ====================

def test_create_access_token():
    """Test JWT token creation"""
    data = {"sub": "testuser", "role": "user"}
    token = create_access_token(data)
    
    # Token should be a string
    assert isinstance(token, str)
    
    # Token should have 3 parts (header.payload.signature)
    assert token.count('.') == 2
    
    # Should be decodable
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "testuser"
    assert payload["role"] == "user"
    assert "exp" in payload

def test_token_expiration():
    """Test token expiration"""
    data = {"sub": "testuser"}
    
    # Create token with short expiration
    expires_delta = timedelta(seconds=-1)  # Already expired
    token = create_access_token(data, expires_delta)
    
    # Decoding should fail due to expiration
    from jose import ExpiredSignatureError
    with pytest.raises(ExpiredSignatureError):
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# ==================== Authentication Endpoint Tests ====================

def test_login_success():
    """Test successful login"""
    response = client.post(
        "/token",
        data={"username": "alice", "password": "secret"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password():
    """Test login with wrong password"""
    response = client.post(
        "/token",
        data={"username": "alice", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_login_nonexistent_user():
    """Test login with non-existent user"""
    response = client.post(
        "/token",
        data={"username": "nonexistent", "password": "secret"}
    )
    
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

# ==================== Public Endpoint Tests ====================

def test_public_status_endpoint():
    """Test public endpoint (no authentication required)"""
    response = client.get("/status")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "timestamp" in data
    assert "total_users" in data

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test_users" in data

# ==================== Protected Endpoint Tests ====================

def test_access_protected_without_token():
    """Test accessing protected endpoint without token"""
    response = client.get("/users/me")
    
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_access_protected_with_invalid_token():
    """Test accessing protected endpoint with invalid token"""
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalidtoken123"}
    )
    
    assert response.status_code == 401

def test_access_protected_with_valid_token(alice_token):
    """Test accessing protected endpoint with valid token"""
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"

# ==================== Role-Based Access Tests ====================

def test_admin_can_list_users(alice_token):
    """Test that admin can list all users"""
    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 3  # alice, bob, charlie

def test_regular_user_cannot_list_users(bob_token):
    """Test that regular user cannot list all users"""
    response = client.get(
        "/users",
        headers={"Authorization": f"Bearer {bob_token}"}
    )
    
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]

def test_admin_can_delete_user(alice_token):
    """Test that admin can delete users"""
    # First, create a test user
    test_user = {
        "username": "testdelete",
        "email": "test@example.com",
        "password": "TestPass123",
        "role": "user"
    }
    client.post("/register", json=test_user)
    
    # Delete the user
    response = client.delete(
        "/users/testdelete",
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]

def test_regular_user_cannot_delete_user(bob_token):
    """Test that regular user cannot delete users"""
    response = client.delete(
        "/users/alice",
        headers={"Authorization": f"Bearer {bob_token}"}
    )
    
    assert response.status_code == 403

def test_admin_cannot_delete_themselves(alice_token):
    """Test that admin cannot delete their own account"""
    response = client.delete(
        "/users/alice",
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    
    assert response.status_code == 400
    assert "Cannot delete yourself" in response.json()["detail"]

# ==================== Security Scope Tests ====================

def test_user_with_read_scope_can_read_items(bob_token):
    """Test user with items:read scope can read items"""
    response = client.get(
        "/users/me/items",
        headers={"Authorization": f"Bearer {bob_token}"}
    )
    
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)

def test_user_without_write_scope_cannot_create_items(bob_token):
    """Test user without items:write scope cannot create items"""
    response = client.post(
        "/items?title=Test Item",
        headers={"Authorization": f"Bearer {bob_token}"}
    )
    
    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]

def test_admin_with_write_scope_can_create_items(alice_token):
    """Test admin with items:write scope can create items"""
    response = client.post(
        "/items?title=Admin Item",
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Admin Item"
    assert data["owner"] == "alice"

# ==================== Registration Tests ====================

def test_register_new_user():
    """Test user registration"""
    new_user = {
        "username": "testuser123",
        "email": "testuser@example.com",
        "full_name": "Test User",
        "password": "SecurePass123",
        "role": "user"
    }
    
    response = client.post("/register", json=new_user)
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == new_user["username"]
    assert data["email"] == new_user["email"]
    assert "password" not in data  # Password should not be in response

def test_register_duplicate_username():
    """Test registering with existing username"""
    new_user = {
        "username": "alice",  # Already exists
        "email": "newalice@example.com",
        "password": "SecurePass123",
        "role": "user"
    }
    
    response = client.post("/register", json=new_user)
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_register_weak_password():
    """Test registration with weak password"""
    new_user = {
        "username": "weakpass",
        "email": "weak@example.com",
        "password": "weak",  # Too short, no uppercase, no digit
        "role": "user"
    }
    
    response = client.post("/register", json=new_user)
    
    assert response.status_code == 422  # Validation error

def test_register_then_login():
    """Test registering a new user and then logging in"""
    # Register
    new_user = {
        "username": "newbie",
        "email": "newbie@example.com",
        "password": "NewPass123",
        "role": "user"
    }
    
    register_response = client.post("/register", json=new_user)
    assert register_response.status_code == 201
    
    # Login
    login_response = client.post(
        "/token",
        data={"username": "newbie", "password": "NewPass123"}
    )
    
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

# ==================== Admin Operations Tests ====================

def test_admin_can_update_user_role(alice_token):
    """Test that admin can update user roles"""
    # Create a test user
    new_user = {
        "username": "roletestuser",
        "email": "roletest@example.com",
        "password": "TestPass123",
        "role": "user"
    }
    client.post("/register", json=new_user)
    
    # Update role to admin
    response = client.put(
        "/users/roletestuser/role?new_role=admin",
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"

def test_admin_can_get_specific_user(alice_token):
    """Test that admin can get any user by username"""
    response = client.get(
        "/users/bob",
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "bob"

def test_regular_user_cannot_get_specific_user(bob_token):
    """Test that regular user cannot get other users"""
    response = client.get(
        "/users/alice",
        headers={"Authorization": f"Bearer {bob_token}"}
    )
    
    assert response.status_code == 403

# ==================== Error Handling Tests ====================

def test_malformed_token():
    """Test with malformed token"""
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer not.a.valid.token"}
    )
    
    assert response.status_code == 401

def test_missing_bearer_prefix():
    """Test with token missing Bearer prefix"""
    response = client.get(
        "/users/me",
        headers={"Authorization": "sometoken"}
    )
    
    assert response.status_code == 403

def test_get_nonexistent_user(alice_token):
    """Test getting a user that doesn't exist"""
    response = client.get(
        "/users/nonexistent",
        headers={"Authorization": f"Bearer {alice_token}"}
    )
    
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]

# ==================== Run Tests ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
