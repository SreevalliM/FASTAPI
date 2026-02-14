"""
🔧 Manual Testing Examples
===========================
Demonstrates manual testing patterns and how they compare to pytest automation.

This script shows:
- Manual API testing with TestClient
- How dependency overrides work interactively
- Comparing manual vs automated testing
- Quick verification of endpoints

Run:
    python manual_test.py
"""

from fastapi.testclient import TestClient
from unittest.mock import Mock
import importlib.util
import sys

# Import the API module
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
User = api_module.User

# Create test client
client = TestClient(app)

print("\n" + "="*60)
print("🔧 Manual Testing Examples")
print("="*60 + "\n")

# ==================== Example 1: Basic Endpoint Testing ====================

print("📝 Example 1: Testing Basic Endpoints")
print("-" * 60)

response = client.get("/")
print(f"GET / -> Status: {response.status_code}")
print(f"Response: {response.json()}")
print()

response = client.get("/health")
print(f"GET /health -> Status: {response.status_code}")
print(f"Response: {response.json()}")
print()

# ==================== Example 2: Testing Users ====================

print("\n📝 Example 2: Testing User Endpoints")
print("-" * 60)

response = client.get("/users")
print(f"GET /users -> Status: {response.status_code}")
print(f"Found {len(response.json())} users")
for user in response.json():
    print(f"  - {user['name']} ({user['email']})")
print()

response = client.get("/users/1")
print(f"GET /users/1 -> Status: {response.status_code}")
print(f"User: {response.json()['name']}")
print()

response = client.get("/users/999")
print(f"GET /users/999 (non-existent) -> Status: {response.status_code}")
print(f"Error: {response.json()['detail']}")
print()

# ==================== Example 3: Testing Products ====================

print("\n📝 Example 3: Testing Product Endpoints")
print("-" * 60)

response = client.get("/products")
print(f"GET /products -> Status: {response.status_code}")
print(f"Found {len(response.json())} products")
for product in response.json():
    print(f"  - {product['name']}: ${product['price']} (Stock: {product['stock']})")
print()

# ==================== Example 4: Testing Authentication ====================

print("\n📝 Example 4: Testing Authentication")
print("-" * 60)

# Try without authentication
response = client.get("/users/me")
print(f"GET /users/me (no auth) -> Status: {response.status_code}")
print(f"Expected 403 (Forbidden)")
print()

# Try with valid token (user_id as token)
headers = {"Authorization": "Bearer 1"}
response = client.get("/users/me", headers=headers)
print(f"GET /users/me (with token) -> Status: {response.status_code}")
if response.status_code == 200:
    print(f"Current user: {response.json()['name']}")
print()

# Try admin endpoint as regular user
headers = {"Authorization": "Bearer 2"}  # Bob (not admin)
response = client.post(
    "/products",
    json={"name": "Test Product", "price": 99.99, "stock": 10},
    headers=headers
)
print(f"POST /products (non-admin) -> Status: {response.status_code}")
print(f"Expected 403 (Forbidden): {response.json()['detail']}")
print()

# ==================== Example 5: Dependency Override ====================

print("\n📝 Example 5: Testing with Dependency Override")
print("-" * 60)

# Create mock database
mock_db = {
    "users": {
        99: {"id": 99, "name": "Mock User", "email": "mock@test.com", "role": "user"}
    },
    "products": {}
}

# Override database dependency
app.dependency_overrides[get_database] = lambda: mock_db

print("Overriding database with mock data...")
response = client.get("/users")
print(f"GET /users (with override) -> Status: {response.status_code}")
print(f"Users in mock database: {len(response.json())}")
for user in response.json():
    print(f"  - {user['name']} (ID: {user['id']})")

# Clear override
app.dependency_overrides.clear()
print("\nCleared database override")

response = client.get("/users")
print(f"GET /users (normal) -> Status: {response.status_code}")
print(f"Users in normal database: {len(response.json())}")
print()

# ==================== Example 6: Bypassing Authentication ====================

print("\n📝 Example 6: Bypassing Authentication with Override")
print("-" * 60)

# Create mock user
mock_user = User(id=99, name="Mock Admin", email="mock@test.com", role="admin")

# Override authentication dependencies
app.dependency_overrides[get_current_user] = lambda: mock_user
app.dependency_overrides[require_admin] = lambda: mock_user

print(f"Overriding auth with mock admin: {mock_user.name}")

# Now we can access admin endpoints without actual token
response = client.post(
    "/products",
    json={"name": "Test Product", "price": 49.99, "stock": 5}
)
print(f"POST /products (bypassed auth) -> Status: {response.status_code}")
if response.status_code == 201:
    print(f"Created product: {response.json()['name']}")

# Clear overrides
app.dependency_overrides.clear()
print("\nCleared authentication override")
print()

# ==================== Example 7: Mocking External API ====================

print("\n📝 Example 7: Mocking External API")
print("-" * 60)

# Create mock external API
mock_api_client = Mock()
mock_api_client.get_exchange_rate.return_value = 2.0

# Override external API dependency
app.dependency_overrides[get_external_api_client] = lambda: mock_api_client

print("Overriding external API with mock (rate: 2.0)...")
response = client.get("/convert/100?from_currency=USD&to_currency=EUR")
print(f"GET /convert/100 -> Status: {response.status_code}")
data = response.json()
print(f"Converted: ${data['amount']} {data['from']} = ${data['converted']} {data['to']}")
print(f"Rate used: {data['rate']}")

# Verify mock was called
print(f"\nMock API called {mock_api_client.get_exchange_rate.call_count} time(s)")
print(f"Called with: {mock_api_client.get_exchange_rate.call_args}")

# Clear override
app.dependency_overrides.clear()
print("\nCleared external API override")
print()

# ==================== Example 8: Testing Order Creation ====================

print("\n📝 Example 8: Testing Order Creation")
print("-" * 60)

# Setup authentication
mock_user = User(id=1, name="Test User", email="test@test.com", role="user")
app.dependency_overrides[get_current_user] = lambda: mock_user

# Check initial product stock
response = client.get("/products/1")
initial_stock = response.json()["stock"]
print(f"Initial stock of product 1: {initial_stock}")

# Create order
response = client.post(
    "/orders",
    json={"user_id": 1, "product_id": 1, "quantity": 2}
)
print(f"\nPOST /orders -> Status: {response.status_code}")
if response.status_code == 201:
    order = response.json()
    print(f"Order created:")
    print(f"  - Order ID: {order['id']}")
    print(f"  - Quantity: {order['quantity']}")
    print(f"  - Total: ${order['total_price']}")

# Check updated stock
response = client.get("/products/1")
new_stock = response.json()["stock"]
print(f"\nNew stock of product 1: {new_stock}")
print(f"Stock reduced by: {initial_stock - new_stock}")

# Try to order more than available
response = client.post(
    "/orders",
    json={"user_id": 1, "product_id": 1, "quantity": 99999}
)
print(f"\nPOST /orders (insufficient stock) -> Status: {response.status_code}")
print(f"Error: {response.json()['detail']}")

# Clear override
app.dependency_overrides.clear()
print()

# ==================== Example 9: Testing Error Cases ====================

print("\n📝 Example 9: Testing Error Cases")
print("-" * 60)

# Invalid user ID
response = client.get("/users/abc")
print(f"GET /users/abc (invalid ID) -> Status: {response.status_code}")

# Non-existent product
response = client.get("/products/999")
print(f"GET /products/999 (not found) -> Status: {response.status_code}")
print(f"Error: {response.json()['detail']}")

# Invalid token
headers = {"Authorization": "Bearer invalid_token"}
response = client.get("/users/me", headers=headers)
print(f"GET /users/me (invalid token) -> Status: {response.status_code}")
print(f"Error: {response.json()['detail']}")
print()

# ==================== Summary ====================

print("\n" + "="*60)
print("✅ Manual Testing Complete!")
print("="*60)
print("\n📊 What We Tested:")
print("  ✓ Basic endpoints (GET, POST, DELETE)")
print("  ✓ Authentication and authorization")
print("  ✓ Dependency overrides (database, auth)")
print("  ✓ External API mocking")
print("  ✓ Order creation with stock management")
print("  ✓ Error handling and edge cases")
print("\n💡 Key Takeaways:")
print("  • TestClient makes testing easy")
print("  • Dependency overrides isolate tests")
print("  • Mocking prevents external calls")
print("  • Always cleanup overrides!")
print("\n🧪 Ready to write automated tests?")
print("  Run: pytest test_testing_basics.py -v")
print("="*60 + "\n")
