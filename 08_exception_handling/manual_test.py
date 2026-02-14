"""
Manual Test Script for Exception Handling
========================================

This script tests the exception handling endpoints manually.
"""

import requests
from typing import Dict, Any
import json


BASE_URL = "http://127.0.0.1:8000"


def print_response(title: str, response: requests.Response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"TEST: {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print()


def test_basic_endpoints():
    """Test basic exception handling endpoints"""
    print("\n" + "="*60)
    print("TESTING BASIC EXCEPTION HANDLING")
    print("="*60)
    
    # 1. Get existing item
    response = requests.get(f"{BASE_URL}/items/1")
    print_response("Get Existing Item (ID: 1)", response)
    
    # 2. Get non-existent item (404 error)
    response = requests.get(f"{BASE_URL}/items/999")
    print_response("Get Non-existent Item (404 Error)", response)
    
    # 3. Create valid item
    item_data = {
        "name": "Test Keyboard",
        "price": 129.99,
        "quantity": 25
    }
    response = requests.post(f"{BASE_URL}/items", json=item_data)
    print_response("Create Valid Item", response)
    
    # 4. Create item with negative price (validation error)
    invalid_item = {
        "name": "Invalid Item",
        "price": -50,
        "quantity": 10
    }
    response = requests.post(f"{BASE_URL}/items", json=invalid_item)
    print_response("Create Item with Invalid Price (Validation Error)", response)
    
    # 5. Create item with special characters
    invalid_item = {
        "name": "Item<script>alert('xss')</script>",
        "price": 50,
        "quantity": 10
    }
    response = requests.post(f"{BASE_URL}/items", json=invalid_item)
    print_response("Create Item with Special Characters (Validation Error)", response)
    
    # 6. Update item
    update_data = {
        "name": "Updated Mouse",
        "price": 29.99,
        "quantity": 60
    }
    response = requests.put(f"{BASE_URL}/items/2", json=update_data)
    print_response("Update Existing Item", response)
    
    # 7. Update non-existent item
    response = requests.put(f"{BASE_URL}/items/999", json=update_data)
    print_response("Update Non-existent Item (404 Error)", response)
    
    # 8. Try to delete item with quantity
    response = requests.delete(f"{BASE_URL}/items/1")
    print_response("Delete Item with Quantity (400 Error)", response)
    
    # 9. Protected endpoint without key
    response = requests.get(f"{BASE_URL}/protected")
    print_response("Protected Endpoint without API Key (401 Error)", response)
    
    # 10. Protected endpoint with invalid key
    response = requests.get(
        f"{BASE_URL}/protected",
        headers={"X-API-Key": "invalid-key"}
    )
    print_response("Protected Endpoint with Invalid Key (403 Error)", response)
    
    # 11. Protected endpoint with valid key
    response = requests.get(
        f"{BASE_URL}/protected",
        headers={"X-API-Key": "secret-key-123"}
    )
    print_response("Protected Endpoint with Valid Key", response)
    
    # 12. Division by zero
    response = requests.get(f"{BASE_URL}/divide/10/0")
    print_response("Division by Zero (400 Error)", response)
    
    # 13. Successful division
    response = requests.get(f"{BASE_URL}/divide/10/2")
    print_response("Successful Division", response)
    
    # 14. List items with pagination
    response = requests.get(f"{BASE_URL}/items?skip=0&limit=2")
    print_response("List Items with Pagination", response)
    
    # 15. Invalid pagination parameters
    response = requests.get(f"{BASE_URL}/items?skip=-1&limit=101")
    print_response("Invalid Pagination Parameters (Validation Error)", response)


def test_custom_exceptions():
    """Test custom exception handling endpoints"""
    print("\n" + "="*60)
    print("TESTING CUSTOM EXCEPTION HANDLING")
    print("="*60)
    
    # 1. Get existing item
    response = requests.get(f"{BASE_URL}/items/1")
    print_response("Get Existing Item", response)
    
    # 2. Get non-existent item (custom ItemNotFoundError)
    response = requests.get(f"{BASE_URL}/items/999")
    print_response("Get Non-existent Item (Custom ItemNotFoundError)", response)
    
    # 3. Create item with valid category
    item_data = {
        "name": "Programming Book",
        "price": 59.99,
        "quantity": 30,
        "category": "books"
    }
    response = requests.post(f"{BASE_URL}/items", json=item_data)
    print_response("Create Item with Valid Category", response)
    
    # 4. Create duplicate item (ItemAlreadyExistsError)
    duplicate_item = {
        "name": "Laptop",  # Already exists
        "price": 999.99,
        "quantity": 5,
        "category": "electronics"
    }
    response = requests.post(f"{BASE_URL}/items", json=duplicate_item)
    print_response("Create Duplicate Item (ItemAlreadyExistsError)", response)
    
    # 5. Create item with invalid category
    invalid_category = {
        "name": "New Item",
        "price": 99.99,
        "quantity": 10,
        "category": "invalid_category"
    }
    response = requests.post(f"{BASE_URL}/items", json=invalid_category)
    print_response("Create Item with Invalid Category (ValueError)", response)
    
    # 6. Place successful order
    order_data = {
        "item_id": 1,
        "quantity": 2
    }
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    print_response("Place Successful Order", response)
    
    # 7. Order non-existent item
    order_data = {
        "item_id": 999,
        "quantity": 1
    }
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    print_response("Order Non-existent Item (ItemNotFoundError)", response)
    
    # 8. Order with insufficient stock
    order_data = {
        "item_id": 1,
        "quantity": 9999
    }
    response = requests.post(f"{BASE_URL}/orders", json=order_data)
    print_response("Order with Insufficient Stock (InsufficientStockError)", response)
    
    # 9. Try to delete item with stock
    response = requests.delete(f"{BASE_URL}/items/1")
    print_response("Delete Item with Stock (InvalidOperationError)", response)
    
    # 10. List all items
    response = requests.get(f"{BASE_URL}/items")
    print_response("List All Items", response)
    
    # 11. Test unexpected error
    response = requests.get(f"{BASE_URL}/test-error")
    print_response("Trigger Unexpected Error (Catch-all Handler)", response)
    
    # 12. Test ValueError
    response = requests.get(f"{BASE_URL}/test-value-error")
    print_response("Trigger ValueError (ValueError Handler)", response)
    
    # 13. Multiple validation errors
    invalid_data = {
        "name": "",
        "price": -10,
        "quantity": -5,
        "category": "electronics"
    }
    response = requests.post(f"{BASE_URL}/items", json=invalid_data)
    print_response("Multiple Validation Errors", response)


def main():
    """Run manual tests"""
    print("\n" + "="*60)
    print("FASTAPI EXCEPTION HANDLING - MANUAL TESTS")
    print("="*60)
    print("\nMake sure the API is running on http://127.0.0.1:8000")
    print("Start with: python 08_exception_handling_basic.py")
    print("Or: python 08_custom_exceptions.py")
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/")
        
        if "Exception Handling" in response.json().get("message", ""):
            if "Basic" in response.json()["message"]:
                print("\n✅ Testing Basic Exception Handling API")
                test_basic_endpoints()
            elif "Custom" in response.json()["message"]:
                print("\n✅ Testing Custom Exception Handling API")
                test_custom_exceptions()
            else:
                print("\n⚠️  Unknown API version")
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the API")
        print("Please start the API first:")
        print("  python 08_exception_handling_basic.py")
        print("  or")
        print("  python 08_custom_exceptions.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    main()
