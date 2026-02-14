"""
Manual testing script for E-commerce API
Run this after starting the API server
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_response(title: str, response: requests.Response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print()


def test_products():
    """Test product endpoints"""
    print("\n" + "="*60)
    print("📦 TESTING PRODUCTS")
    print("="*60)
    
    # Create products
    products = [
        {
            "name": "Gaming Laptop",
            "description": "High-performance gaming laptop",
            "price": 1999.99,
            "stock": 10,
            "category": "Electronics"
        },
        {
            "name": "Wireless Mouse",
            "description": "Ergonomic wireless mouse",
            "price": 49.99,
            "stock": 100,
            "category": "Electronics"
        },
        {
            "name": "USB-C Cable",
            "description": "Fast charging USB-C cable",
            "price": 19.99,
            "stock": 200,
            "category": "Accessories"
        }
    ]
    
    created_products = []
    for product in products:
        response = requests.post(f"{BASE_URL}/products", json=product)
        print_response(f"Create Product: {product['name']}", response)
        if response.status_code == 201:
            created_products.append(response.json())
    
    # List all products
    response = requests.get(f"{BASE_URL}/products")
    print_response("List All Products", response)
    
    # Filter by category
    response = requests.get(f"{BASE_URL}/products?category=Electronics")
    print_response("Filter by Category (Electronics)", response)
    
    # Get specific product
    if created_products:
        product_id = created_products[0]["id"]
        response = requests.get(f"{BASE_URL}/products/{product_id}")
        print_response(f"Get Product ID {product_id}", response)
        
        # Update product
        response = requests.put(
            f"{BASE_URL}/products/{product_id}",
            json={"price": 1799.99, "stock": 8}
        )
        print_response(f"Update Product ID {product_id}", response)
    
    # Test error: Product not found
    response = requests.get(f"{BASE_URL}/products/999")
    print_response("Error Test: Product Not Found", response)
    
    return created_products


def test_orders(products: list):
    """Test order endpoints"""
    print("\n" + "="*60)
    print("🛒 TESTING ORDERS")
    print("="*60)
    
    if not products or len(products) < 2:
        print("⚠️  Need at least 2 products to test orders")
        return []
    
    # Create order
    order_data = {
        "customer_name": "Alice Johnson",
        "customer_email": "alice@example.com",
        "items": [
            {"product_id": products[0]["id"], "quantity": 1},
            {"product_id": products[1]["id"], "quantity": 2}
        ]
    }
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    print_response("Create Order", response)
    
    created_orders = []
    if response.status_code == 201:
        created_orders.append(response.json())
    
    # Create another order
    order_data2 = {
        "customer_name": "Bob Smith",
        "customer_email": "bob@example.com",
        "items": [
            {"product_id": products[2]["id"], "quantity": 5}
        ]
    }
    response = requests.post(f"{BASE_URL}/orders", json=order_data2)
    print_response("Create Another Order", response)
    if response.status_code == 201:
        created_orders.append(response.json())
    
    # List all orders
    response = requests.get(f"{BASE_URL}/orders")
    print_response("List All Orders", response)
    
    # Get specific order
    if created_orders:
        order_id = created_orders[0]["id"]
        response = requests.get(f"{BASE_URL}/orders/{order_id}")
        print_response(f"Get Order ID {order_id}", response)
        
        # Update order status
        response = requests.patch(
            f"{BASE_URL}/orders/{order_id}/status",
            json={"status": "confirmed"}
        )
        print_response(f"Update Order Status to Confirmed", response)
        
        response = requests.patch(
            f"{BASE_URL}/orders/{order_id}/status",
            json={"status": "shipped"}
        )
        print_response(f"Update Order Status to Shipped", response)
    
    # Test error: Insufficient stock
    print("\n🧪 Testing Error Handling...")
    response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "customer_name": "Charlie Brown",
            "customer_email": "charlie@example.com",
            "items": [{"product_id": products[0]["id"], "quantity": 1000}]
        }
    )
    print_response("Error Test: Insufficient Stock", response)
    
    # Test error: Invalid product
    response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "customer_name": "David Lee",
            "customer_email": "david@example.com",
            "items": [{"product_id": 999, "quantity": 1}]
        }
    )
    print_response("Error Test: Product Not Found", response)
    
    return created_orders


def test_order_status_transitions(orders: list):
    """Test order status transitions"""
    if not orders:
        return
    
    print("\n" + "="*60)
    print("🔄 TESTING ORDER STATUS TRANSITIONS")
    print("="*60)
    
    # Create a new order for testing
    response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "customer_name": "Test User",
            "customer_email": "test@example.com",
            "items": [{"product_id": 1, "quantity": 1}]
        }
    )
    
    if response.status_code == 201:
        order_id = response.json()["id"]
        
        # Valid transitions
        statuses = ["confirmed", "shipped", "delivered"]
        for status in statuses:
            response = requests.patch(
                f"{BASE_URL}/orders/{order_id}/status",
                json={"status": status}
            )
            print_response(f"Transition to {status.upper()}", response)
        
        # Try invalid transition (from delivered back to pending)
        response = requests.patch(
            f"{BASE_URL}/orders/{order_id}/status",
            json={"status": "pending"}
        )
        print_response("Error Test: Invalid Status Transition", response)


def test_inventory_tracking():
    """Test that inventory is tracked correctly"""
    print("\n" + "="*60)
    print("📊 TESTING INVENTORY TRACKING")
    print("="*60)
    
    # Create a product with known stock
    product_data = {
        "name": "Inventory Test Product",
        "price": 99.99,
        "stock": 20,
        "category": "Test"
    }
    response = requests.post(f"{BASE_URL}/products", json=product_data)
    product_id = response.json()["id"]
    initial_stock = response.json()["stock"]
    print_response(f"Created Product (Initial Stock: {initial_stock})", response)
    
    # Create order with 5 items
    response = requests.post(
        f"{BASE_URL}/orders",
        json={
            "customer_name": "Inventory Tester",
            "customer_email": "inventory@example.com",
            "items": [{"product_id": product_id, "quantity": 5}]
        }
    )
    print_response("Created Order (5 items)", response)
    
    # Check updated stock
    response = requests.get(f"{BASE_URL}/products/{product_id}")
    updated_stock = response.json()["stock"]
    print_response(f"Check Stock After Order (Should be {initial_stock - 5})", response)
    
    if updated_stock == initial_stock - 5:
        print("✅ Inventory tracking working correctly!")
    else:
        print(f"❌ Inventory tracking issue: Expected {initial_stock - 5}, got {updated_stock}")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 E-COMMERCE API MANUAL TESTING SUITE")
    print("="*80)
    print("\nMake sure the API server is running at http://localhost:8000")
    print("Start it with: python ecommerce_api.py")
    
    try:
        # Test health endpoint
        response = requests.get(f"{BASE_URL}/health")
        print_response("Health Check", response)
        
        # Run tests
        products = test_products()
        orders = test_orders(products)
        test_order_status_transitions(orders)
        test_inventory_tracking()
        
        print("\n" + "="*80)
        print("✅ MANUAL TESTING COMPLETE!")
        print("="*80)
        print("\n💡 TIP: Check the API server console to see background email logs")
        print("📚 Visit http://localhost:8000/docs for interactive API documentation")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API server")
        print("Make sure the server is running: python ecommerce_api.py")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


if __name__ == "__main__":
    main()
