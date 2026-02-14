# 🧪 Testing FastAPI with Pytest - Complete Tutorial

Learn how to write comprehensive tests for FastAPI applications using pytest, TestClient, dependency overrides, and mocking.

---

## 📋 Table of Contents

1. [Introduction to Testing](#introduction)
2. [TestClient Basics](#testclient-basics)
3. [Testing Different HTTP Methods](#testing-http-methods)
4. [Dependency Overrides](#dependency-overrides)
5. [Mocking External Services](#mocking-external-services)
6. [Database Mocking](#database-mocking)
7. [Fixtures and Reusability](#fixtures-and-reusability)
8. [Parametrized Tests](#parametrized-tests)
9. [Authentication Testing](#authentication-testing)
10. [Best Practices](#best-practices)

---

## 🎯 Introduction to Testing {#introduction}

### Why Test?

- **Confidence**: Know your code works as expected
- **Refactoring**: Change code without fear
- **Documentation**: Tests show how to use your API
- **Regression Prevention**: Catch bugs before production

### Testing Pyramid

```
        /\          E2E Tests (Few)
       /  \         
      /____\        Integration Tests (Some)
     /      \       
    /________\      Unit Tests (Many)
```

### Testing Tools

- **pytest**: Testing framework
- **TestClient**: FastAPI's test client
- **unittest.mock**: Mocking library
- **pytest-cov**: Coverage reporting
- **pytest-asyncio**: Async test support

---

## 🔧 TestClient Basics {#testclient-basics}

### Setup TestClient

```python
from fastapi.testclient import TestClient
from myapp import app

client = TestClient(app)
```

### Your First Test

```python
def test_root():
    """Test the root endpoint"""
    response = client.get("/")
    
    # Assert status code
    assert response.status_code == 200
    
    # Assert response data
    assert response.json() == {"message": "Hello World"}
```

### Common Assertions

```python
# Status Codes
assert response.status_code == 200  # OK
assert response.status_code == 201  # Created
assert response.status_code == 400  # Bad Request
assert response.status_code == 404  # Not Found
assert response.status_code == 500  # Server Error

# Response Data
data = response.json()
assert data["name"] == "Alice"
assert "id" in data
assert len(data["items"]) > 0

# Headers
assert "content-type" in response.headers
assert response.headers["content-type"] == "application/json"
```

---

## 📨 Testing Different HTTP Methods {#testing-http-methods}

### GET Requests

```python
def test_get_user():
    response = client.get("/users/1")
    assert response.status_code == 200
```

### POST Requests

```python
def test_create_user():
    response = client.post(
        "/users",
        json={"name": "Alice", "email": "alice@example.com"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Alice"
```

### PUT/PATCH Requests

```python
def test_update_user():
    response = client.put(
        "/users/1",
        json={"name": "Alice Updated"}
    )
    assert response.status_code == 200
```

### DELETE Requests

```python
def test_delete_user():
    response = client.delete("/users/1")
    assert response.status_code == 204  # No Content
```

### With Headers

```python
def test_with_auth_header():
    headers = {"Authorization": "Bearer token123"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 200
```

### With Query Parameters

```python
def test_with_query_params():
    response = client.get("/search?q=alice&limit=10")
    assert response.status_code == 200
```

---

## 🔄 Dependency Overrides {#dependency-overrides}

### Why Override Dependencies?

- **Isolation**: Test without external dependencies
- **Speed**: Avoid slow database/API calls
- **Control**: Use predictable test data
- **Flexibility**: Test edge cases easily

### Basic Override

```python
# Original dependency
def get_database():
    return {"users": real_database}

# In test
def test_with_override():
    # Create test data
    test_db = {"users": {"1": {"name": "Test User"}}}
    
    # Override dependency
    app.dependency_overrides[get_database] = lambda: test_db
    
    try:
        response = client.get("/users/1")
        assert response.json()["name"] == "Test User"
    finally:
        # Always cleanup!
        app.dependency_overrides.clear()
```

### Override Authentication

```python
from myapp import get_current_user, User

def test_bypass_auth():
    # Create mock user
    mock_user = User(id=1, name="Test", role="admin")
    
    # Bypass authentication
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    try:
        # Access protected endpoint without token
        response = client.get("/admin/dashboard")
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()
```

### Multiple Overrides

```python
def test_multiple_overrides():
    app.dependency_overrides[get_database] = lambda: test_db
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_settings] = lambda: test_settings
    
    try:
        response = client.get("/complex-endpoint")
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()
```

### Context Manager for Safety

```python
from contextlib import contextmanager

@contextmanager
def override_dependency(dependency, override):
    """Ensures cleanup even if test fails"""
    app.dependency_overrides[dependency] = override
    try:
        yield
    finally:
        app.dependency_overrides.pop(dependency, None)

def test_with_context_manager():
    with override_dependency(get_database, lambda: test_db):
        response = client.get("/users")
        assert response.status_code == 200
    # Automatic cleanup!
```

---

## 🎭 Mocking External Services {#mocking-external-services}

### Why Mock?

- Don't call real APIs in tests
- Avoid costs (payment APIs)
- Test error conditions
- Fast and reliable tests

### Mock with unittest.mock

```python
from unittest.mock import Mock

def test_external_api():
    # Create mock
    mock_api = Mock()
    mock_api.get_exchange_rate.return_value = 1.5
    
    # Override dependency
    app.dependency_overrides[get_api_client] = lambda: mock_api
    
    try:
        response = client.get("/convert/100")
        assert response.json()["rate"] == 1.5
        
        # Verify mock was called
        mock_api.get_exchange_rate.assert_called_once()
    finally:
        app.dependency_overrides.clear()
```

### Mock Multiple Return Values

```python
def test_multiple_calls():
    mock_api = Mock()
    # Return different values for each call
    mock_api.fetch_data.side_effect = [
        {"status": "ok"},
        {"status": "pending"},
        {"status": "completed"}
    ]
    
    app.dependency_overrides[get_api] = lambda: mock_api
    
    try:
        # First call
        response = client.get("/status/1")
        assert response.json()["status"] == "ok"
        
        # Second call
        response = client.get("/status/2")
        assert response.json()["status"] == "pending"
    finally:
        app.dependency_overrides.clear()
```

### Mock Exceptions

```python
def test_api_failure():
    mock_api = Mock()
    mock_api.fetch_data.side_effect = ConnectionError("API unavailable")
    
    app.dependency_overrides[get_api] = lambda: mock_api
    
    try:
        response = client.get("/data")
        assert response.status_code == 503  # Service Unavailable
    finally:
        app.dependency_overrides.clear()
```

### Patch Functions

```python
from unittest.mock import patch

@patch('myapp.send_email')
def test_signup(mock_send_email):
    """Prevent actually sending email"""
    mock_send_email.return_value = True
    
    response = client.post("/signup", json={
        "email": "test@example.com",
        "password": "secret"
    })
    
    assert response.status_code == 201
    # Verify email was "sent"
    mock_send_email.assert_called_once()
```

---

## 💾 Database Mocking {#database-mocking}

### In-Memory Test Database

```python
@pytest.fixture
def test_db():
    """Create fresh test database for each test"""
    return {
        "users": {},
        "products": {},
        "orders": []
    }

def test_with_test_db(test_db):
    app.dependency_overrides[get_database] = lambda: test_db
    
    try:
        # Database starts empty
        response = client.get("/users")
        assert len(response.json()) == 0
        
        # Create user
        response = client.post("/users", json={"name": "Alice"})
        assert response.status_code == 201
        
        # Now we have one user
        response = client.get("/users")
        assert len(response.json()) == 1
    finally:
        app.dependency_overrides.clear()
```

### Mock Database Connection

```python
from unittest.mock import Mock

def test_database_query():
    # Mock database connection
    mock_db = Mock()
    mock_db.execute.return_value = [
        (1, "Alice", "alice@example.com"),
        (2, "Bob", "bob@example.com")
    ]
    
    app.dependency_overrides[get_db_conn] = lambda: mock_db
    
    try:
        response = client.get("/users")
        assert len(response.json()) == 2
        
        # Verify query was executed
        mock_db.execute.assert_called()
    finally:
        app.dependency_overrides.clear()
```

### SQLite Test Database

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def test_db_session():
    """Create temporary SQLite database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()

def test_with_sqlite(test_db_session):
    app.dependency_overrides[get_db] = lambda: test_db_session
    
    try:
        response = client.post("/users", json={"name": "Alice"})
        assert response.status_code == 201
    finally:
        app.dependency_overrides.clear()
```

---

## 🔧 Fixtures and Reusability {#fixtures-and-reusability}

### Basic Fixture

```python
@pytest.fixture
def sample_user():
    """Provide a sample user for tests"""
    return {"id": 1, "name": "Alice", "email": "alice@example.com"}

def test_with_fixture(sample_user):
    assert sample_user["name"] == "Alice"
```

### Setup/Teardown Fixtures

```python
@pytest.fixture
def authenticated_client():
    """Setup: Login and get token"""
    response = client.post("/login", json={
        "username": "test",
        "password": "secret"
    })
    token = response.json()["token"]
    
    # Return client with auth header
    client.headers = {"Authorization": f"Bearer {token}"}
    
    yield client
    
    # Teardown: Logout
    client.post("/logout")
    client.headers = {}

def test_protected_endpoint(authenticated_client):
    response = authenticated_client.get("/profile")
    assert response.status_code == 200
```

### Fixture Scope

```python
@pytest.fixture(scope="module")
def database():
    """Created once per test module"""
    db = setup_database()
    yield db
    db.cleanup()

@pytest.fixture(scope="function")  # Default
def fresh_data():
    """Created for each test function"""
    return {"count": 0}

@pytest.fixture(scope="session")
def config():
    """Created once per test session"""
    return load_config()
```

### Fixture Composition

```python
@pytest.fixture
def database():
    return setup_test_db()

@pytest.fixture
def admin_user(database):
    """Fixture that uses another fixture"""
    user = User(name="Admin", role="admin")
    database.add(user)
    return user

def test_admin_action(admin_user, database):
    # Both fixtures are available
    assert admin_user.role == "admin"
```

---

## 🔢 Parametrized Tests {#parametrized-tests}

### Basic Parametrization

```python
@pytest.mark.parametrize("user_id,expected_name", [
    (1, "Alice"),
    (2, "Bob"),
    (3, "Charlie"),
])
def test_get_user(user_id, expected_name):
    """Test runs 3 times with different parameters"""
    response = client.get(f"/users/{user_id}")
    assert response.json()["name"] == expected_name
```

### Multiple Parameters

```python
@pytest.mark.parametrize("method,endpoint,status", [
    ("GET", "/users", 200),
    ("GET", "/products", 200),
    ("POST", "/users", 201),
    ("DELETE", "/users/1", 204),
])
def test_endpoints(method, endpoint, status):
    response = client.request(method, endpoint)
    assert response.status_code == status
```

### Parametrize Invalid Inputs

```python
@pytest.mark.parametrize("invalid_email", [
    "notanemail",
    "@example.com",
    "user@",
    "user space@example.com",
    "",
])
def test_invalid_emails(invalid_email):
    response = client.post("/users", json={
        "name": "Test",
        "email": invalid_email
    })
    assert response.status_code == 422  # Validation Error
```

### Parametrize with IDs

```python
@pytest.mark.parametrize("input,expected", [
    pytest.param(100, 150, id="usd_to_eur"),
    pytest.param(50, 75, id="small_amount"),
    pytest.param(1000, 1500, id="large_amount"),
])
def test_conversion(input, expected):
    response = client.get(f"/convert/{input}")
    assert response.json()["converted"] == expected
```

---

## 🔐 Authentication Testing {#authentication-testing}

### Test Login

```python
def test_login_success():
    response = client.post("/token", data={
        "username": "alice",
        "password": "secret"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure():
    response = client.post("/token", data={
        "username": "alice",
        "password": "wrong"
    })
    
    assert response.status_code == 401
```

### Test Protected Endpoints

```python
def test_protected_without_auth():
    response = client.get("/profile")
    assert response.status_code == 403  # Forbidden

def test_protected_with_auth():
    # Get token
    login = client.post("/token", data={
        "username": "alice",
        "password": "secret"
    })
    token = login.json()["access_token"]
    
    # Use token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/profile", headers=headers)
    assert response.status_code == 200
```

### Bypass Authentication in Tests

```python
@pytest.fixture
def bypass_auth():
    """Fixture to bypass authentication"""
    mock_user = User(id=1, name="Test User", role="user")
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.clear()

def test_endpoint(bypass_auth):
    # No need for actual authentication
    response = client.get("/profile")
    assert response.status_code == 200
```

### Test Different Roles

```python
@pytest.mark.parametrize("role,expected_status", [
    ("admin", 200),
    ("user", 403),
    ("guest", 403),
])
def test_admin_endpoint(role, expected_status):
    mock_user = User(id=1, name="Test", role=role)
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    try:
        response = client.get("/admin/dashboard")
        assert response.status_code == expected_status
    finally:
        app.dependency_overrides.clear()
```

---

## ✅ Best Practices {#best-practices}

### 1. Test Isolation

```python
# ❌ Bad: Tests depend on each other
def test_create_user():
    client.post("/users", json={"name": "Alice"})

def test_get_user():
    # Depends on previous test
    response = client.get("/users/1")
    assert response.json()["name"] == "Alice"

# ✅ Good: Each test is independent
def test_create_user():
    response = client.post("/users", json={"name": "Alice"})
    user_id = response.json()["id"]
    
    # Verify in same test
    response = client.get(f"/users/{user_id}")
    assert response.json()["name"] == "Alice"
```

### 2. Clear Test Names

```python
# ❌ Bad
def test_1():
    ...

# ✅ Good
def test_create_user_with_valid_data_returns_201():
    ...

def test_create_user_with_duplicate_email_returns_400():
    ...
```

### 3. Arrange-Act-Assert Pattern

```python
def test_create_order():
    # Arrange: Setup test data
    user_id = create_test_user()
    product_id = create_test_product()
    
    # Act: Perform action
    response = client.post("/orders", json={
        "user_id": user_id,
        "product_id": product_id,
        "quantity": 2
    })
    
    # Assert: Verify results
    assert response.status_code == 201
    assert response.json()["quantity"] == 2
```

### 4. Always Cleanup

```python
def test_with_cleanup():
    app.dependency_overrides[get_db] = lambda: test_db
    
    try:
        # Test code
        response = client.get("/users")
        assert response.status_code == 200
    finally:
        # Always cleanup, even if test fails
        app.dependency_overrides.clear()
```

### 5. Use Fixtures for Reusability

```python
@pytest.fixture
def auth_headers():
    token = get_test_token()
    return {"Authorization": f"Bearer {token}"}

def test_endpoint_1(auth_headers):
    response = client.get("/endpoint1", headers=auth_headers)
    assert response.status_code == 200

def test_endpoint_2(auth_headers):
    response = client.get("/endpoint2", headers=auth_headers)
    assert response.status_code == 200
```

### 6. Test Edge Cases

```python
def test_edge_cases():
    # Empty string
    response = client.post("/users", json={"name": ""})
    assert response.status_code == 422
    
    # Very long string
    response = client.post("/users", json={"name": "a" * 10000})
    assert response.status_code == 422
    
    # Null value
    response = client.post("/users", json={"name": None})
    assert response.status_code == 422
```

### 7. Test Error Handling

```python
def test_server_error_handling():
    # Simulate server error
    def raise_error():
        raise Exception("Database unavailable")
    
    app.dependency_overrides[get_db] = raise_error
    
    try:
        response = client.get("/users")
        assert response.status_code == 500
        assert "error" in response.json()
    finally:
        app.dependency_overrides.clear()
```

---

## 🎯 Complete Example

```python
import pytest
from fastapi.testclient import TestClient
from myapp import app, get_database, get_current_user, User

client = TestClient(app)

# Fixtures
@pytest.fixture
def test_db():
    return {"users": {}, "products": {}}

@pytest.fixture
def admin_user():
    return User(id=1, name="Admin", role="admin")

@pytest.fixture
def setup_admin(admin_user):
    app.dependency_overrides[get_current_user] = lambda: admin_user
    yield
    app.dependency_overrides.clear()

# Tests
def test_create_user_success(test_db, setup_admin):
    app.dependency_overrides[get_database] = lambda: test_db
    
    try:
        response = client.post("/users", json={
            "name": "Alice",
            "email": "alice@example.com"
        })
        
        assert response.status_code == 201
        assert response.json()["name"] == "Alice"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.parametrize("invalid_email", [
    "notanemail",
    "@example.com",
    "user@"
])
def test_create_user_invalid_email(invalid_email, setup_admin):
    response = client.post("/users", json={
        "name": "Test",
        "email": invalid_email
    })
    assert response.status_code == 422
```

---

## 📊 Running Tests

```bash
# Run all tests
pytest

# Run specific file
pytest test_users.py

# Run specific test
pytest test_users.py::test_create_user

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=myapp

# Run tests matching pattern
pytest -k "user"

# Run marked tests
pytest -m integration

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

---

## 🎓 Summary

**Key Concepts:**

1. **TestClient**: Make HTTP requests to your API
2. **Dependency Overrides**: Replace real dependencies in tests
3. **Mocking**: Simulate external services
4. **Fixtures**: Reusable test setup
5. **Parametrization**: Test multiple scenarios
6. **Isolation**: Each test should be independent

**Remember:**
- Always cleanup overrides
- Test happy paths AND error cases
- Use clear, descriptive test names
- Keep tests fast and reliable
- Aim for high coverage, but focus on important paths

Happy Testing! 🧪✨
