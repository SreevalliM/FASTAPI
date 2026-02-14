"""
🧪 Comprehensive FastAPI Testing with Pytest
=============================================
Demonstrates:
1. TestClient usage
2. Dependency overrides
3. Database mocking
4. External service mocking
5. Fixtures and parametrization
6. Testing authentication

Run tests:
    pytest test_testing_basics.py -v

Run specific test:
    pytest test_testing_basics.py::test_root -v

Run with coverage:
    pytest test_testing_basics.py -v --cov=11_api_for_testing

Run with output:
    pytest test_testing_basics.py -v -s
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import importlib.util
import sys

# ==================== Import Module ====================

# Import module with number prefix
spec = importlib.util.spec_from_file_location(
    "api_for_testing", 
    "11_api_for_testing.py"
)
api_module = importlib.util.module_from_spec(spec)
sys.modules["api_for_testing"] = api_module
spec.loader.exec_module(api_module)

# Import from loaded module
app = api_module.app
get_database = api_module.get_database
get_current_user = api_module.get_current_user
require_admin = api_module.require_admin
get_external_api_client = api_module.get_external_api_client
get_db_connection = api_module.get_db_connection
User = api_module.User
DatabaseConnection = api_module.DatabaseConnection

# ==================== Test Client Setup ====================

client = TestClient(app)

# ==================== PART 1: Basic TestClient Usage ====================

def test_root():
    """Test simple GET endpoint"""
    response = client.get("/")
    
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to Testing Example API",
        "status": "ok"
    }

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"

def test_list_users():
    """Test listing users"""
    response = client.get("/users")
    
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 2  # At least Alice and Bob
    assert any(u["name"] == "Alice" for u in users)

def test_get_user_success():
    """Test getting existing user"""
    response = client.get("/users/1")
    
    assert response.status_code == 200
    user = response.json()
    assert user["name"] == "Alice"
    assert user["email"] == "alice@example.com"

def test_get_user_not_found():
    """Test getting non-existent user returns 404"""
    response = client.get("/users/999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_list_products():
    """Test listing products"""
    response = client.get("/products")
    
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 2
    assert any(p["name"] == "Laptop" for p in products)

# ==================== PART 2: Testing with Headers and Authentication ====================

def test_get_current_user_without_auth():
    """Test protected endpoint without authentication"""
    response = client.get("/users/me")
    
    # Should return 401 because HTTPBearer security requires auth header
    assert response.status_code == 401

def test_get_current_user_with_valid_token():
    """Test protected endpoint with valid authentication"""
    # Use user_id as token (simplified auth)
    headers = {"Authorization": "Bearer 1"}  
    response = client.get("/users/me", headers=headers)
    
    assert response.status_code == 200
    user = response.json()
    assert user["name"] == "Alice"

def test_get_current_user_with_invalid_token():
    """Test protected endpoint with invalid token"""
    headers = {"Authorization": "Bearer invalid"}
    response = client.get("/users/me", headers=headers)
    
    assert response.status_code == 401

def test_create_product_without_admin():
    """Test admin endpoint without admin role"""
    headers = {"Authorization": "Bearer 2"}  # Bob is not admin
    response = client.post(
        "/products",
        json={"name": "Keyboard", "price": 59.99, "stock": 20},
        headers=headers
    )
    
    assert response.status_code == 403
    assert "admin" in response.json()["detail"].lower()

# ==================== PART 3: Dependency Override - Mock Database ====================

@pytest.fixture
def mock_db():
    """Create a mock database for testing"""
    return {
        "users": {
            1: {"id": 1, "name": "Test User", "email": "test@example.com", "role": "user"},
            2: {"id": 2, "name": "Test Admin", "email": "admin@example.com", "role": "admin"},
        },
        "products": {
            1: {"id": 1, "name": "Test Product", "price": 99.99, "stock": 5},
        }
    }

def test_with_database_override(mock_db):
    """
    Test with dependency override - replace database
    This demonstrates how to override dependencies in tests
    """
    
    # Override the get_database dependency
    app.dependency_overrides[get_database] = lambda: mock_db
    
    try:
        # Now requests will use mock_db
        response = client.get("/users")
        
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 2
        assert users[0]["name"] == "Test User"
        
        # Test product with mock data
        response = client.get("/products/1")
        assert response.status_code == 200
        assert response.json()["name"] == "Test Product"
        
    finally:
        # Clear overrides after test
        app.dependency_overrides.clear()

def test_isolated_database():
    """
    Test with isolated database to avoid side effects
    Each test gets its own database
    """
    isolated_db = {
        "users": {
            100: {"id": 100, "name": "Isolated User", "email": "isolated@example.com", "role": "admin"}
        },
        "products": {}
    }
    
    app.dependency_overrides[get_database] = lambda: isolated_db
    
    try:
        response = client.get("/users")
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "Isolated User"
    finally:
        app.dependency_overrides.clear()

# ==================== PART 4: Dependency Override - Bypass Authentication ====================

def test_bypass_authentication():
    """
    Override authentication dependency to bypass auth in tests
    Useful for testing endpoints without dealing with tokens
    """
    
    # Create a mock user
    mock_user = User(id=99, name="Mock User", email="mock@example.com", role="user")
    
    # Override authentication dependency
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    try:
        # Access protected endpoint without Authorization header
        response = client.get("/users/me")
        
        assert response.status_code == 200
        user = response.json()
        assert user["name"] == "Mock User"
        assert user["id"] == 99
        
    finally:
        app.dependency_overrides.clear()

def test_bypass_admin_check():
    """
    Override admin requirement to test admin endpoints
    """
    
    # Create mock admin user
    mock_admin = User(id=88, name="Mock Admin", email="admin@example.com", role="admin")
    
    # Override both authentication dependencies
    app.dependency_overrides[get_current_user] = lambda: mock_admin
    app.dependency_overrides[require_admin] = lambda: mock_admin
    
    try:
        # Create product without worrying about authentication
        response = client.post(
            "/products",
            json={"name": "Test Product", "price": 49.99, "stock": 10}
        )
        
        assert response.status_code == 201
        product = response.json()
        assert product["name"] == "Test Product"
        
    finally:
        app.dependency_overrides.clear()

# ==================== PART 5: Mocking External Services ====================

def test_currency_conversion_with_mock():
    """
    Test currency conversion with mocked external API
    Demonstrates mocking external service dependencies
    """
    
    # Create mock API client
    mock_api_client = Mock()
    mock_api_client.get_exchange_rate.return_value = 1.5
    
    # Override external API dependency
    app.dependency_overrides[get_external_api_client] = lambda: mock_api_client
    
    try:
        response = client.get("/convert/100?from_currency=USD&to_currency=EUR")
        
        assert response.status_code == 200
        data = response.json()
        assert data["amount"] == 100
        assert data["rate"] == 1.5
        assert data["converted"] == 150.0
        
        # Verify mock was called
        mock_api_client.get_exchange_rate.assert_called_once_with("USD", "EUR")
        
    finally:
        app.dependency_overrides.clear()

def test_currency_conversion_multiple_rates():
    """
    Test multiple currency conversions with different mocked rates
    """
    
    mock_api_client = Mock()
    # Mock different rates for different calls
    mock_api_client.get_exchange_rate.side_effect = [0.85, 0.73, 1.18]
    
    app.dependency_overrides[get_external_api_client] = lambda: mock_api_client
    
    try:
        # First call
        response = client.get("/convert/100?from_currency=USD&to_currency=EUR")
        assert response.json()["rate"] == 0.85
        
        # Second call
        response = client.get("/convert/100?from_currency=USD&to_currency=GBP")
        assert response.json()["rate"] == 0.73
        
        # Third call
        response = client.get("/convert/100?from_currency=EUR&to_currency=USD")
        assert response.json()["rate"] == 1.18
        
    finally:
        app.dependency_overrides.clear()

# ==================== PART 6: Mocking Database Connections ====================

def test_user_stats_with_mocked_db():
    """
    Test database query with mocked DB connection
    Demonstrates mocking database dependencies
    """
    
    # Create mock database connection
    mock_db_conn = Mock(spec=DatabaseConnection)
    mock_db_conn.execute_query.return_value = [("users", 100), ("admins", 10)]
    
    # Override database connection dependency
    app.dependency_overrides[get_db_connection] = lambda: mock_db_conn
    
    try:
        response = client.get("/stats/users")
        
        assert response.status_code == 200
        stats = response.json()
        # The endpoint doesn't actually use the mock query, but demonstrates pattern
        assert "total_users" in stats
        
    finally:
        app.dependency_overrides.clear()

# ==================== PART 7: Fixtures for Reusable Test Data ====================

@pytest.fixture
def admin_user():
    """Fixture providing admin user"""
    return User(id=1, name="Admin", email="admin@example.com", role="admin")

@pytest.fixture
def regular_user():
    """Fixture providing regular user"""
    return User(id=2, name="User", email="user@example.com", role="user")

@pytest.fixture
def setup_admin_auth(admin_user):
    """Fixture that sets up admin authentication"""
    app.dependency_overrides[get_current_user] = lambda: admin_user
    app.dependency_overrides[require_admin] = lambda: admin_user
    yield
    app.dependency_overrides.clear()

def test_create_user_with_fixture(setup_admin_auth):
    """
    Test using fixture for authentication setup
    Cleaner than manually managing overrides
    """
    response = client.post(
        "/users",
        json={"name": "New User", "email": "new@example.com", "role": "user"}
    )
    
    assert response.status_code == 201
    user = response.json()
    assert user["name"] == "New User"

def test_delete_product_with_fixture(setup_admin_auth):
    """Test delete operation using auth fixture"""
    # First get a product ID
    response = client.get("/products")
    if response.json():
        product_id = response.json()[0]["id"]
        
        response = client.delete(f"/products/{product_id}")
        assert response.status_code == 204

# ==================== PART 8: Parametrized Tests ====================

@pytest.mark.parametrize("user_id,expected_name", [
    (1, "Alice"),
    (2, "Bob"),
])
def test_get_user_parametrized(user_id, expected_name):
    """
    Test multiple users with parametrization
    Runs the test once for each parameter set
    """
    response = client.get(f"/users/{user_id}")
    
    assert response.status_code == 200
    assert response.json()["name"] == expected_name

@pytest.mark.parametrize("endpoint", [
    "/",
    "/health",
    "/users",
    "/products",
])
def test_public_endpoints_accessible(endpoint):
    """Test that public endpoints are accessible"""
    response = client.get(endpoint)
    assert response.status_code == 200

@pytest.mark.parametrize("invalid_id", [999, 0, -1, 10000])
def test_get_user_invalid_ids(invalid_id):
    """Test various invalid user IDs"""
    response = client.get(f"/users/{invalid_id}")
    assert response.status_code == 404

# ==================== PART 9: Testing Order Creation (Complex Logic) ====================

def test_create_order_success():
    """Test successful order creation"""
    # Setup authentication
    mock_user = User(id=1, name="Test User", email="test@example.com", role="user")
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    # Also need to setup database for order to work
    test_db = {
        "users": {1: {"id": 1, "name": "Test User", "email": "test@example.com", "role": "user"}},
        "products": {1: {"id": 1, "name": "Test Product", "price": 10.0, "stock": 10}}
    }
    app.dependency_overrides[get_database] = lambda: test_db
    
    try:
        # Get initial product stock
        response = client.get("/products/1")
        initial_stock = response.json()["stock"]
        
        # Create order
        response = client.post(
            "/orders",
            json={"user_id": 1, "product_id": 1, "quantity": 2}
        )
        
        assert response.status_code == 201
        order = response.json()
        assert order["quantity"] == 2
        assert order["user_id"] == 1
        assert order["product_id"] == 1
        assert "total_price" in order
        
        # Verify stock was reduced
        response = client.get("/products/1")
        new_stock = response.json()["stock"]
        assert new_stock == initial_stock - 2
        
    finally:
        app.dependency_overrides.clear()

def test_create_order_insufficient_stock():
    """Test order creation with insufficient stock"""
    mock_user = User(id=1, name="Test User", email="test@example.com", role="user")
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    # Setup database with limited stock
    test_db = {
        "users": {1: {"id": 1, "name": "Test User", "email": "test@example.com", "role": "user"}},
        "products": {1: {"id": 1, "name": "Test Product", "price": 10.0, "stock": 5}}
    }
    app.dependency_overrides[get_database] = lambda: test_db
    
    try:
        # Try to order more than available stock
        response = client.post(
            "/orders",
            json={"user_id": 1, "product_id": 1, "quantity": 99999}
        )
        
        assert response.status_code == 400
        assert "insufficient stock" in response.json()["detail"].lower()
        
    finally:
        app.dependency_overrides.clear()

def test_create_order_invalid_product():
    """Test order creation with non-existent product"""
    mock_user = User(id=1, name="Test User", email="test@example.com", role="user")
    app.dependency_overrides[get_current_user] = lambda: mock_user
    
    # Setup database with user but no products
    test_db = {
        "users": {1: {"id": 1, "name": "Test User", "email": "test@example.com", "role": "user"}},
        "products": {}
    }
    app.dependency_overrides[get_database] = lambda: test_db
    
    try:
        response = client.post(
            "/orders",
            json={"user_id": 1, "product_id": 999, "quantity": 1}
        )
        
        assert response.status_code == 404
        assert "product" in response.json()["detail"].lower()
        
    finally:
        app.dependency_overrides.clear()

# ==================== PART 10: Testing with Pytest Marks ====================

@pytest.mark.slow
def test_slow_operation():
    """
    Mark slow tests
    Run with: pytest -v -m slow
    Skip with: pytest -v -m "not slow"
    """
    response = client.get("/products")
    assert response.status_code == 200

@pytest.mark.integration
def test_integration_example():
    """
    Mark integration tests
    Run with: pytest -v -m integration
    """
    response = client.get("/health")
    assert response.status_code == 200

# ==================== PART 11: Setup and Teardown ====================

class TestWithSetupTeardown:
    """
    Test class demonstrating setup and teardown
    """
    
    @classmethod
    def setup_class(cls):
        """Run once before all tests in class"""
        print("\n🔧 Setting up test class...")
        cls.test_data = {"initialized": True}
    
    @classmethod
    def teardown_class(cls):
        """Run once after all tests in class"""
        print("\n🧹 Tearing down test class...")
    
    def setup_method(self):
        """Run before each test method"""
        self.request_count = 0
    
    def teardown_method(self):
        """Run after each test method"""
        app.dependency_overrides.clear()
    
    def test_with_setup(self):
        """Test that uses setup data"""
        assert self.test_data["initialized"] is True
        self.request_count += 1
        response = client.get("/")
        assert response.status_code == 200

# ==================== PART 12: Testing Response Models ====================

def test_user_response_model_validation():
    """Test that response conforms to Pydantic model"""
    response = client.get("/users/1")
    
    assert response.status_code == 200
    user = response.json()
    
    # Verify all required fields are present
    assert "id" in user
    assert "name" in user
    assert "email" in user
    assert "role" in user
    
    # Verify types
    assert isinstance(user["id"], int)
    assert isinstance(user["name"], str)
    assert "@" in user["email"]  # Basic email validation

def test_product_response_model_validation():
    """Test product response model"""
    # First get list of products to ensure one exists
    response = client.get("/products")
    products = response.json()
    
    if not products:
        # If no products, skip this test
        import pytest
        pytest.skip("No products available for testing")
    
    product_id = products[0]["id"]
    response = client.get(f"/products/{product_id}")
    
    assert response.status_code == 200  
    product = response.json()
    
    assert product["price"] > 0  # Price must be positive
    assert product["stock"] >= 0  # Stock must be non-negative

# ==================== PART 13: Context Manager for Overrides ====================

from contextlib import contextmanager

@contextmanager
def override_dependency(dependency, override):
    """
    Context manager for dependency overrides
    Ensures cleanup even if test fails
    """
    app.dependency_overrides[dependency] = override
    try:
        yield
    finally:
        app.dependency_overrides.pop(dependency, None)

def test_with_context_manager():
    """Test using context manager for cleaner override management"""
    mock_user = User(id=50, name="Context User", email="context@example.com", role="admin")
    
    with override_dependency(get_current_user, lambda: mock_user):
        with override_dependency(require_admin, lambda: mock_user):
            response = client.post(
                "/products",
                json={"name": "Context Product", "price": 29.99, "stock": 5}
            )
            assert response.status_code == 201

# ==================== PART 14: Async Testing (if needed) ====================

@pytest.mark.asyncio
async def test_async_example():
    """
    Example of async test (requires pytest-asyncio)
    Install: pip install pytest-asyncio
    """
    # For async endpoints, use httpx.AsyncClient instead
    # from httpx import AsyncClient
    # async with AsyncClient(app=app, base_url="http://test") as ac:
    #     response = await ac.get("/")
    #     assert response.status_code == 200
    
    # For now, just use sync client
    response = client.get("/")
    assert response.status_code == 200

# ==================== Summary ====================

"""
Key Testing Concepts Demonstrated:

1. TestClient Usage:
   - Basic GET/POST/DELETE requests
   - Headers and authentication
   - Status code assertions
   - Response data validation

2. Dependency Overrides:
   - Override database dependencies
   - Bypass authentication
   - Mock admin requirements
   - Isolated test data

3. Mocking:
   - Mock external APIs
   - Mock database connections
   - Mock service responses
   - Verify mock calls

4. Fixtures:
   - Reusable test data
   - Setup/teardown
   - Fixture composition
   - Parametrized fixtures

5. Best Practices:
   - Test isolation
   - Clear test names
   - Arrange-Act-Assert pattern
   - Cleanup after tests
   - Context managers for safety

Run specific test categories:
    pytest test_testing_basics.py -k "auth" -v          # Tests with 'auth' in name
    pytest test_testing_basics.py -k "mock" -v          # Tests with 'mock' in name
    pytest test_testing_basics.py -m integration -v     # Integration tests only
    pytest test_testing_basics.py --collect-only        # List all tests
"""
