# 🧪 Testing with Pytest

Learn comprehensive testing strategies for FastAPI applications using pytest, TestClient, dependency overrides, and mocking.

## 🎯 What You'll Learn

- ✅ **TestClient**: Make HTTP requests to test your API
- 🔄 **Dependency Overrides**: Replace dependencies in tests
- 🎭 **Mocking**: Simulate external services and databases
- 🔧 **Fixtures**: Create reusable test components
- 🔢 **Parametrization**: Test multiple scenarios efficiently
- 🔐 **Authentication Testing**: Test protected endpoints
- 💾 **Database Mocking**: Test without real databases

---

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
# From project root
source ../fastapi-env/bin/activate
```

### 2. Install Dependencies
```bash
pip install pytest pytest-cov pytest-asyncio httpx
```

### 3. Run the Tests
```bash
cd 11_testing_pytest
pytest test_testing_basics.py -v
```

### 4. Run with Coverage
```bash
pytest test_testing_basics.py --cov=11_api_for_testing --cov-report=html
```

### 5. View Coverage Report
```bash
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

---

## 📂 Files in This Module

| File | Description |
|------|-------------|
| `11_api_for_testing.py` | Sample API with various endpoints for testing |
| `test_testing_basics.py` | Comprehensive test suite with examples |
| `11_TESTING_TUTORIAL.md` | Complete testing tutorial |
| `TESTING_CHEATSHEET.md` | Quick reference for testing patterns |
| `manual_test.py` | Manual testing examples |
| `quickstart.sh` | Quick setup script |

---

## 📖 Tutorial Structure

### Part 1: TestClient Basics
Learn how to use FastAPI's TestClient to make HTTP requests and assert responses.

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

### Part 2: Dependency Overrides
Replace dependencies with test doubles to isolate your tests.

```python
def test_with_mock_db():
    test_db = {"users": {1: {"name": "Test User"}}}
    app.dependency_overrides[get_database] = lambda: test_db
    
    try:
        response = client.get("/users/1")
        assert response.json()["name"] == "Test User"
    finally:
        app.dependency_overrides.clear()
```

### Part 3: Mocking External Services
Simulate external APIs and services without making real calls.

```python
from unittest.mock import Mock

def test_external_api():
    mock_api = Mock()
    mock_api.get_data.return_value = {"status": "ok"}
    
    app.dependency_overrides[get_api_client] = lambda: mock_api
    
    try:
        response = client.get("/data")
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()
```

### Part 4: Testing Authentication
Test protected endpoints with and without authentication.

```python
def test_protected_endpoint():
    mock_user = User(id=1, name="Test", role="admin")
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    try:
        response = client.get("/admin/dashboard")
        assert response.status_code == 200
    finally:
        app.dependency_overrides.clear()
```

---

## 🧪 Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run specific file
pytest test_testing_basics.py

# Run specific test
pytest test_testing_basics.py::test_root

# Run with verbose output
pytest -v

# Run with detailed output
pytest -vv
```

### Advanced Commands

```bash
# Run with coverage
pytest --cov=11_api_for_testing --cov-report=term-missing

# Run tests matching pattern
pytest -k "auth" -v

# Run marked tests only
pytest -m integration

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Collect tests without running
pytest --collect-only
```

### Running Specific Test Categories

```bash
# Tests with 'mock' in name
pytest -k "mock" -v

# Tests with 'override' in name
pytest -k "override" -v

# Tests with 'auth' in name
pytest -k "auth" -v

# Integration tests (if marked)
pytest -m integration -v

# Slow tests (if marked)
pytest -m slow -v
```

---

## 📊 Test Coverage

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=11_api_for_testing

# HTML report
pytest --cov=11_api_for_testing --cov-report=html

# XML report (for CI/CD)
pytest --cov=11_api_for_testing --cov-report=xml
```

### Coverage Goals

- **Aim for 80%+** overall coverage
- **Focus on critical paths** rather than 100%
- **Test error cases** not just happy paths
- **Don't test framework code** (FastAPI internals)

---

## 🎯 What's Tested

### Endpoints Tested

✅ Basic GET/POST/DELETE operations  
✅ Query parameters and headers  
✅ Request/response validation  
✅ Error handling (404, 400, 500)  
✅ Authentication and authorization  
✅ Database operations  
✅ External API calls  

### Testing Techniques Demonstrated

1. **Simple endpoint testing**
2. **Testing with authentication**
3. **Dependency injection overrides**
4. **Database mocking**
5. **External service mocking**
6. **Parametrized tests**
7. **Fixtures and reusability**
8. **Setup and teardown**
9. **Context managers for safety**
10. **Response model validation**

---

## 🔬 Example Test Cases

### Test Simple Endpoint
```python
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Test POST Request
```python
def test_create_user(setup_admin_auth):
    response = client.post("/users", json={
        "name": "Alice",
        "email": "alice@example.com"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "Alice"
```

### Test Error Handling
```python
def test_user_not_found():
    response = client.get("/users/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
```

### Test with Mock
```python
def test_with_mock_api():
    mock_api = Mock()
    mock_api.get_rate.return_value = 1.5
    
    app.dependency_overrides[get_api] = lambda: mock_api
    
    try:
        response = client.get("/convert/100")
        assert response.json()["converted"] == 150.0
    finally:
        app.dependency_overrides.clear()
```

---

## 🛠️ Best Practices

### 1. Test Isolation
Each test should be independent and not rely on other tests.

### 2. Clear Test Names
Use descriptive names that explain what is being tested.

```python
# ❌ Bad
def test_1():
    ...

# ✅ Good
def test_create_user_with_valid_data_returns_201():
    ...
```

### 3. Arrange-Act-Assert Pattern
Structure tests clearly:

```python
def test_example():
    # Arrange: Setup test data
    user_data = {"name": "Alice"}
    
    # Act: Perform action
    response = client.post("/users", json=user_data)
    
    # Assert: Verify results
    assert response.status_code == 201
```

### 4. Always Cleanup
Use try/finally or context managers to ensure cleanup.

```python
def test_with_cleanup():
    app.dependency_overrides[get_db] = lambda: test_db
    try:
        # Test code
        pass
    finally:
        app.dependency_overrides.clear()
```

### 5. Use Fixtures
Create reusable test components with fixtures.

```python
@pytest.fixture
def admin_user():
    return User(id=1, name="Admin", role="admin")

def test_with_fixture(admin_user):
    assert admin_user.role == "admin"
```

---

## 📚 Additional Resources

### Documentation
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

### Tutorials
- See `11_TESTING_TUTORIAL.md` for complete tutorial
- See `TESTING_CHEATSHEET.md` for quick reference

### Related Modules
- `03_dependency_injection/` - Understanding dependencies
- `05_authentication/` - Testing auth flows
- `09_ecommerce_api/` - Complex API testing

---

## 🎓 Learning Path

1. **Read** the tutorial: `11_TESTING_TUTORIAL.md`
2. **Study** the test file: `test_testing_basics.py`
3. **Run** the tests: `pytest test_testing_basics.py -v`
4. **Experiment** with the API: `python 11_api_for_testing.py`
5. **Try** manual testing: `python manual_test.py`
6. **Reference** the cheatsheet when needed

---

## 💡 Tips

- Start with simple tests, add complexity gradually
- Test the happy path first, then error cases
- Mock external dependencies to keep tests fast
- Use parametrization to test multiple scenarios
- Aim for meaningful tests, not just high coverage
- Run tests frequently during development
- Use `pytest -x` to stop on first failure when debugging

---

## 🐛 Troubleshooting

### Import Errors
```bash
# Make sure you're in the correct directory
cd 11_testing_pytest

# Check Python path
python -c "import sys; print(sys.path)"
```

### Tests Not Found
```bash
# Use explicit file name
pytest test_testing_basics.py

# Check test discovery
pytest --collect-only
```

### Fixture Not Found
```bash
# Make sure fixture is in same file or conftest.py
# Check fixture name matches parameter name
```

### Dependency Override Not Working
```python
# Make sure to clear overrides after test
try:
    # test code
finally:
    app.dependency_overrides.clear()
```

---

## ✅ What's Next?

After mastering testing:

1. **Learn CI/CD**: Automate testing in pipelines
2. **Performance Testing**: Load testing with Locust
3. **Integration Testing**: Test with real databases
4. **End-to-End Testing**: Test full user workflows
5. **Test-Driven Development**: Write tests first

---

## 🎯 Practice Exercises

1. Add tests for a new endpoint
2. Create a fixture for database setup
3. Mock an external weather API
4. Test error cases (400, 500)
5. Achieve 90%+ test coverage
6. Write parametrized tests for validation
7. Test with async operations

---

## 📞 Need Help?

- Check the tutorial for detailed explanations
- Review the cheatsheet for quick patterns
- Run `pytest --help` for command options
- Check existing tests for examples

Happy Testing! 🧪✨
