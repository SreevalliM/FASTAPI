# 🧪 Testing with Pytest - Cheat Sheet

Quick reference for FastAPI testing patterns, TestClient, dependency overrides, and mocking.

---

## 📦 Setup & Installation

```bash
# Install pytest
pip install pytest pytest-cov pytest-asyncio

# Install for async testing
pip install httpx

# Run tests
pytest                          # All tests
pytest test_file.py            # Specific file
pytest test_file.py::test_name # Specific test
pytest -v                      # Verbose
pytest -s                      # Show print
pytest -x                      # Stop on first failure
pytest --lf                    # Run last failed
```

---

## 🔧 TestClient Basics

### Setup

```python
from fastapi.testclient import TestClient
from myapp import app

client = TestClient(app)
```

### HTTP Methods

```python
# GET
response = client.get("/users")
response = client.get("/users/1")
response = client.get("/search?q=alice&limit=10")

# POST
response = client.post("/users", json={"name": "Alice"})

# PUT
response = client.put("/users/1", json={"name": "Updated"})

# PATCH
response = client.patch("/users/1", json={"age": 30})

# DELETE
response = client.delete("/users/1")
```

### Headers

```python
# With headers
headers = {"Authorization": "Bearer token123"}
response = client.get("/protected", headers=headers)

# Custom headers
headers = {"X-API-Key": "secret", "X-Request-ID": "123"}
response = client.get("/api", headers=headers)
```

### Assertions

```python
# Status codes
assert response.status_code == 200  # OK
assert response.status_code == 201  # Created
assert response.status_code == 204  # No Content
assert response.status_code == 400  # Bad Request
assert response.status_code == 401  # Unauthorized
assert response.status_code == 403  # Forbidden
assert response.status_code == 404  # Not Found
assert response.status_code == 422  # Validation Error
assert response.status_code == 500  # Server Error

# Response data
data = response.json()
assert data["name"] == "Alice"
assert "id" in data
assert len(data["items"]) > 0
assert data["count"] == 5

# Headers
assert "content-type" in response.headers
assert response.headers["content-type"] == "application/json"
```

---

## 🔄 Dependency Overrides

### Basic Override

```python
from myapp import app, get_database

def test_with_override():
    # Create test data
    test_db = {"users": {1: {"name": "Test User"}}}
    
    # Override dependency
    app.dependency_overrides[get_database] = lambda: test_db
    
    try:
        response = client.get("/users/1")
        assert response.json()["name"] == "Test User"
    finally:
        # Always cleanup!
        app.dependency_overrides.clear()
```

### Override Multiple Dependencies

```python
def test_multiple_overrides():
    app.dependency_overrides[get_database] = lambda: test_db
    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_settings] = lambda: test_settings
    
    try:
        response = client.get("/endpoint")
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()
```

### Context Manager (Cleaner)

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
```

### Override Authentication

```python
from myapp import get_current_user, User

def test_bypass_auth():
    mock_user = User(id=1, name="Test", role="admin")
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    try:
        # Access protected endpoint without token
        response = client.get("/admin/dashboard")
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()
```

---

## 🎭 Mocking with unittest.mock

### Mock Return Value

```python
from unittest.mock import Mock

def test_with_mock():
    # Create mock
    mock_api = Mock()
    mock_api.get_data.return_value = {"status": "ok"}
    
    # Override dependency
    app.dependency_overrides[get_api_client] = lambda: mock_api
    
    try:
        response = client.get("/data")
        assert response.json()["status"] == "ok"
        
        # Verify mock was called
        mock_api.get_data.assert_called_once()
    finally:
        app.dependency_overrides.clear()
```

### Mock Multiple Return Values

```python
def test_multiple_returns():
    mock_api = Mock()
    # Return different values for each call
    mock_api.fetch.side_effect = ["first", "second", "third"]
    
    app.dependency_overrides[get_api] = lambda: mock_api
    
    try:
        assert client.get("/data").json() == "first"
        assert client.get("/data").json() == "second"
        assert client.get("/data").json() == "third"
    finally:
        app.dependency_overrides.clear()
```

### Mock Exception

```python
def test_mock_exception():
    mock_api = Mock()
    mock_api.fetch.side_effect = ConnectionError("API unavailable")
    
    app.dependency_overrides[get_api] = lambda: mock_api
    
    try:
        response = client.get("/data")
        assert response.status_code == 503
    finally:
        app.dependency_overrides.clear()
```

### Patch Function

```python
from unittest.mock import patch

@patch('myapp.send_email')
def test_signup(mock_send_email):
    mock_send_email.return_value = True
    
    response = client.post("/signup", json={
        "email": "test@example.com"
    })
    
    assert response.status_code == 201
    mock_send_email.assert_called_once()
```

### Verify Mock Calls

```python
mock_api.method.assert_called()              # Called at least once
mock_api.method.assert_called_once()         # Called exactly once
mock_api.method.assert_called_with("arg")    # Called with specific args
mock_api.method.assert_not_called()          # Never called

# Check call count
assert mock_api.method.call_count == 3
```

---

## 💾 Database Mocking

### In-Memory Database

```python
@pytest.fixture
def test_db():
    """Fresh database for each test"""
    return {
        "users": {},
        "products": {}
    }

def test_with_test_db(test_db):
    app.dependency_overrides[get_database] = lambda: test_db
    
    try:
        # Database starts empty
        response = client.get("/users")
        assert len(response.json()) == 0
        
        # Create user
        client.post("/users", json={"name": "Alice"})
        
        # Now we have one user
        response = client.get("/users")
        assert len(response.json()) == 1
    finally:
        app.dependency_overrides.clear()
```

### Mock Database Connection

```python
def test_mock_db_connection():
    mock_db = Mock()
    mock_db.execute.return_value = [
        (1, "Alice"),
        (2, "Bob")
    ]
    
    app.dependency_overrides[get_db_conn] = lambda: mock_db
    
    try:
        response = client.get("/users")
        assert len(response.json()) == 2
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

## 🔧 Fixtures

### Basic Fixture

```python
@pytest.fixture
def sample_user():
    return {"id": 1, "name": "Alice"}

def test_with_fixture(sample_user):
    assert sample_user["name"] == "Alice"
```

### Fixture with Setup/Teardown

```python
@pytest.fixture
def setup_data():
    # Setup
    data = create_test_data()
    
    yield data
    
    # Teardown
    cleanup_test_data()

def test_with_setup(setup_data):
    assert setup_data is not None
```

### Fixture Scope

```python
@pytest.fixture(scope="function")  # Default: per test
def per_test():
    return setup()

@pytest.fixture(scope="class")     # Per test class
def per_class():
    return setup()

@pytest.fixture(scope="module")    # Per test file
def per_module():
    return setup()

@pytest.fixture(scope="session")   # Once per test session
def per_session():
    return setup()
```

### Fixture Composition

```python
@pytest.fixture
def database():
    return setup_database()

@pytest.fixture
def admin_user(database):
    """Fixture using another fixture"""
    user = create_admin(database)
    return user

def test_admin(admin_user, database):
    # Both fixtures available
    assert admin_user.role == "admin"
```

### Auto-use Fixture

```python
@pytest.fixture(autouse=True)
def reset_database():
    """Runs before every test automatically"""
    clear_database()
    yield
    # Cleanup after test
```

---

## 🔢 Parametrized Tests

### Basic Parametrization

```python
@pytest.mark.parametrize("user_id,expected", [
    (1, "Alice"),
    (2, "Bob"),
    (3, "Charlie"),
])
def test_get_user(user_id, expected):
    response = client.get(f"/users/{user_id}")
    assert response.json()["name"] == expected
```

### Multiple Parameters

```python
@pytest.mark.parametrize("method,endpoint,expected", [
    ("GET", "/users", 200),
    ("GET", "/products", 200),
    ("POST", "/users", 201),
])
def test_endpoints(method, endpoint, expected):
    response = client.request(method, endpoint)
    assert response.status_code == expected
```

### Named Parameters

```python
@pytest.mark.parametrize("amount,rate,result", [
    pytest.param(100, 1.5, 150, id="normal"),
    pytest.param(0, 1.5, 0, id="zero"),
    pytest.param(1000, 2.0, 2000, id="large"),
])
def test_conversion(amount, rate, result):
    # Test implementation
    pass
```

---

## 🔐 Authentication Testing

### Test Login

```python
def test_login_success():
    response = client.post("/token", data={
        "username": "alice",
        "password": "secret"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure():
    response = client.post("/token", data={
        "username": "alice",
        "password": "wrong"
    })
    assert response.status_code == 401
```

### Test Protected Endpoint

```python
def test_protected_endpoint():
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

### Bypass Authentication

```python
@pytest.fixture
def bypass_auth():
    mock_user = User(id=1, name="Test", role="admin")
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides.clear()

def test_admin_endpoint(bypass_auth):
    response = client.get("/admin/dashboard")
    assert response.status_code == 200
```

---

## 📏 Test Patterns

### Arrange-Act-Assert

```python
def test_create_user():
    # Arrange: Setup
    user_data = {"name": "Alice", "email": "alice@example.com"}
    
    # Act: Perform action
    response = client.post("/users", json=user_data)
    
    # Assert: Verify
    assert response.status_code == 201
    assert response.json()["name"] == "Alice"
```

### Test Class

```python
class TestUsers:
    def setup_method(self):
        """Run before each test"""
        self.user_data = {"name": "Alice"}
    
    def teardown_method(self):
        """Run after each test"""
        app.dependency_overrides.clear()
    
    def test_create(self):
        response = client.post("/users", json=self.user_data)
        assert response.status_code == 201
```

---

## 🏷️ Pytest Marks

### Mark Tests

```python
@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.skip("Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.platform == "win32", reason="Unix only")
def test_unix_only():
    pass

@pytest.mark.xfail(reason="Known bug")
def test_known_issue():
    pass
```

### Run Marked Tests

```bash
pytest -m slow              # Run slow tests
pytest -m "not slow"        # Skip slow tests
pytest -m integration       # Run integration tests
```

---

## 📊 Coverage

```bash
# Basic coverage
pytest --cov=myapp

# With missing lines
pytest --cov=myapp --cov-report=term-missing

# HTML report
pytest --cov=myapp --cov-report=html

# XML report (CI/CD)
pytest --cov=myapp --cov-report=xml

# Fail if coverage below threshold
pytest --cov=myapp --cov-fail-under=80
```

---

## 🚀 Advanced Patterns

### Async Tests

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200
```

### Monkeypatch

```python
def test_with_monkeypatch(monkeypatch):
    # Set environment variable
    monkeypatch.setenv("API_KEY", "test_key")
    
    # Patch function
    monkeypatch.setattr("myapp.get_api_key", lambda: "test_key")
    
    response = client.get("/data")
    assert response.status_code == 200
```

### Temp Directory

```python
def test_file_upload(tmp_path):
    # tmp_path is a pathlib.Path to temporary directory
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    
    with open(test_file, "rb") as f:
        response = client.post("/upload", files={"file": f})
    
    assert response.status_code == 200
```

---

## 📝 Quick Commands

```bash
# Development
pytest -v                    # Verbose
pytest -s                    # Show print
pytest -x                    # Stop on first failure
pytest --lf                  # Last failed
pytest -k "test_name"        # Match pattern

# Coverage
pytest --cov                 # Basic coverage
pytest --cov-report=html     # HTML report

# Specific tests
pytest test_file.py          # One file
pytest test_file.py::test    # One test
pytest -m mark               # Marked tests

# Debugging
pytest --pdb                 # Drop to debugger on failure
pytest --trace               # Drop to debugger immediately
pytest --collect-only        # List all tests
```

---

## ✅ Best Practices Checklist

- ✅ Each test is independent
- ✅ Clear, descriptive test names
- ✅ Use Arrange-Act-Assert pattern
- ✅ Always cleanup overrides
- ✅ Mock external dependencies
- ✅ Test both success and error cases
- ✅ Use fixtures for reusability
- ✅ Parametrize similar tests
- ✅ Aim for 80%+ coverage
- ✅ Keep tests fast

---

## 🐛 Common Issues

### Dependency override not working
```python
# Always clear after test
finally:
    app.dependency_overrides.clear()
```

### Test order dependency
```python
# Each test should be independent
# Don't rely on previous test state
```

### Import errors
```python
# Use proper imports
import importlib.util
spec = importlib.util.spec_from_file_location("module", "file.py")
```

---

## 📚 Quick Reference

```python
# Setup
from fastapi.testclient import TestClient
client = TestClient(app)

# Make request
response = client.get("/endpoint")

# Assert
assert response.status_code == 200
assert response.json()["key"] == "value"

# Override
app.dependency_overrides[dep] = lambda: mock
try:
    # test code
finally:
    app.dependency_overrides.clear()

# Mock
from unittest.mock import Mock
mock = Mock()
mock.method.return_value = "value"

# Fixture
@pytest.fixture
def data():
    return {"key": "value"}

# Parametrize
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
])
def test(input, expected):
    assert input * 2 == expected
```

---

Happy Testing! 🧪✨
