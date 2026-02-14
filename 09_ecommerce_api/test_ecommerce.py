"""
Test file for E-commerce API
Run with: pytest test_ecommerce.py -v
"""
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ecommerce_api import app, get_db, Base
import pytest

# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_ecommerce.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ==================== Product Tests ====================

def test_create_product():
    """Test creating a new product"""
    response = client.post("/products", json={
        "name": "Test Laptop",
        "description": "A test laptop",
        "price": 999.99,
        "stock": 10,
        "category": "Electronics"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Laptop"
    assert data["price"] == 999.99
    assert data["stock"] == 10
    assert "id" in data
    assert "created_at" in data


def test_create_product_invalid_price():
    """Test creating product with invalid price"""
    response = client.post("/products", json={
        "name": "Invalid Product",
        "price": -10.0,
        "stock": 5
    })
    assert response.status_code == 422  # Validation error


def test_list_products():
    """Test listing all products"""
    # Create test products
    client.post("/products", json={
        "name": "Product 1",
        "price": 100.0,
        "stock": 10,
        "category": "Electronics"
    })
    client.post("/products", json={
        "name": "Product 2",
        "price": 200.0,
        "stock": 5,
        "category": "Books"
    })
    
    response = client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_products_with_filters():
    """Test listing products with category filter"""
    client.post("/products", json={
        "name": "Laptop",
        "price": 1000.0,
        "stock": 5,
        "category": "Electronics"
    })
    client.post("/products", json={
        "name": "Book",
        "price": 20.0,
        "stock": 100,
        "category": "Books"
    })
    
    response = client.get("/products?category=Electronics")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "Electronics"


def test_get_product():
    """Test getting a specific product"""
    create_response = client.post("/products", json={
        "name": "Test Product",
        "price": 50.0,
        "stock": 20
    })
    product_id = create_response.json()["id"]
    
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Test Product"


def test_get_product_not_found():
    """Test getting non-existent product"""
    response = client.get("/products/999")
    assert response.status_code == 404
    data = response.json()
    assert "Product with ID 999 not found" in data["detail"]


def test_update_product():
    """Test updating a product"""
    create_response = client.post("/products", json={
        "name": "Original Name",
        "price": 100.0,
        "stock": 10
    })
    product_id = create_response.json()["id"]
    
    response = client.put(f"/products/{product_id}", json={
        "name": "Updated Name",
        "price": 150.0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["price"] == 150.0
    assert data["stock"] == 10  # Unchanged


def test_delete_product():
    """Test deleting a product"""
    create_response = client.post("/products", json={
        "name": "To Delete",
        "price": 10.0,
        "stock": 5
    })
    product_id = create_response.json()["id"]
    
    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 404


# ==================== Order Tests ====================

def test_create_order():
    """Test creating an order"""
    # Create products first
    product1 = client.post("/products", json={
        "name": "Product 1",
        "price": 100.0,
        "stock": 10
    }).json()
    product2 = client.post("/products", json={
        "name": "Product 2",
        "price": 50.0,
        "stock": 20
    }).json()
    
    response = client.post("/orders", json={
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [
            {"product_id": product1["id"], "quantity": 2},
            {"product_id": product2["id"], "quantity": 1}
        ]
    })
    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "John Doe"
    assert data["total_amount"] == 250.0  # (100 * 2) + (50 * 1)
    assert data["status"] == "pending"
    assert len(data["items"]) == 2


def test_create_order_insufficient_stock():
    """Test creating order with insufficient stock"""
    product = client.post("/products", json={
        "name": "Limited Product",
        "price": 100.0,
        "stock": 5
    }).json()
    
    response = client.post("/orders", json={
        "customer_name": "Jane Doe",
        "customer_email": "jane@example.com",
        "items": [
            {"product_id": product["id"], "quantity": 10}
        ]
    })
    assert response.status_code == 400
    data = response.json()
    assert "Insufficient stock" in data["detail"]


def test_create_order_product_not_found():
    """Test creating order with non-existent product"""
    response = client.post("/orders", json={
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [
            {"product_id": 999, "quantity": 1}
        ]
    })
    assert response.status_code == 404
    data = response.json()
    assert "Product with ID 999 not found" in data["detail"]


def test_order_updates_inventory():
    """Test that creating an order updates product inventory"""
    product = client.post("/products", json={
        "name": "Test Product",
        "price": 100.0,
        "stock": 10
    }).json()
    
    # Create order
    client.post("/orders", json={
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "items": [
            {"product_id": product["id"], "quantity": 3}
        ]
    })
    
    # Check inventory was updated
    updated_product = client.get(f"/products/{product['id']}").json()
    assert updated_product["stock"] == 7  # 10 - 3


def test_list_orders():
    """Test listing all orders"""
    product = client.post("/products", json={
        "name": "Product",
        "price": 50.0,
        "stock": 100
    }).json()
    
    # Create orders
    client.post("/orders", json={
        "customer_name": "Customer 1",
        "customer_email": "customer1@example.com",
        "items": [{"product_id": product["id"], "quantity": 1}]
    })
    client.post("/orders", json={
        "customer_name": "Customer 2",
        "customer_email": "customer2@example.com",
        "items": [{"product_id": product["id"], "quantity": 2}]
    })
    
    response = client.get("/orders")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_order():
    """Test getting a specific order"""
    product = client.post("/products", json={
        "name": "Product",
        "price": 75.0,
        "stock": 50
    }).json()
    
    create_response = client.post("/orders", json={
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "items": [{"product_id": product["id"], "quantity": 1}]
    })
    order_id = create_response.json()["id"]
    
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id


def test_update_order_status():
    """Test updating order status"""
    product = client.post("/products", json={
        "name": "Product",
        "price": 100.0,
        "stock": 10
    }).json()
    
    create_response = client.post("/orders", json={
        "customer_name": "Customer",
        "customer_email": "customer@example.com",
        "items": [{"product_id": product["id"], "quantity": 1}]
    })
    order_id = create_response.json()["id"]
    
    response = client.patch(f"/orders/{order_id}/status", json={
        "status": "confirmed"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "confirmed"


def test_invalid_status_transition():
    """Test invalid order status transition"""
    product = client.post("/products", json={
        "name": "Product",
        "price": 100.0,
        "stock": 10
    }).json()
    
    create_response = client.post("/orders", json={
        "customer_name": "Customer",
        "customer_email": "customer@example.com",
        "items": [{"product_id": product["id"], "quantity": 1}]
    })
    order_id = create_response.json()["id"]
    
    # Set to delivered
    client.patch(f"/orders/{order_id}/status", json={"status": "delivered"})
    
    # Try to change back to pending (should fail)
    response = client.patch(f"/orders/{order_id}/status", json={"status": "pending"})
    assert response.status_code == 400
    data = response.json()
    assert "Cannot change order status" in data["detail"]


def test_cancel_order():
    """Test cancelling an order"""
    product = client.post("/products", json={
        "name": "Product",
        "price": 100.0,
        "stock": 10
    }).json()
    
    create_response = client.post("/orders", json={
        "customer_name": "Customer",
        "customer_email": "customer@example.com",
        "items": [{"product_id": product["id"], "quantity": 1}]
    })
    order_id = create_response.json()["id"]
    
    response = client.delete(f"/orders/{order_id}")
    assert response.status_code == 204
    
    # Verify status is cancelled
    order = client.get(f"/orders/{order_id}").json()
    assert order["status"] == "cancelled"


# ==================== General Tests ====================

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


if __name__ == "__main__":
    print("Run tests with: pytest test_ecommerce.py -v")
    print("Or with coverage: pytest test_ecommerce.py -v --cov=ecommerce_api")
