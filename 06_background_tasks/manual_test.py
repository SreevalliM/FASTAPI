"""
Manual Test Script for Background Tasks
========================================

Run this script to manually test the background tasks examples.
Make sure the server is running first:
  python 06_background_tasks_basic.py
  python 06_email_sending.py
"""

import requests
import time
from typing import Dict, Any
import json

# Configuration
BASIC_API_URL = "http://localhost:8000"
EMAIL_API_URL = "http://localhost:8001"

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_response(response: requests.Response):
    """Print formatted response"""
    print(f"\n📡 Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"📦 Response:")
        print(json.dumps(data, indent=2))
    except:
        print(f"📄 Response: {response.text}")

def test_basic_api():
    """Test basic background tasks API"""
    print_section("Testing Basic Background Tasks API")
    
    # Test 1: Simple notification
    print("\n🧪 Test 1: Simple Notification")
    try:
        response = requests.post(
            f"{BASIC_API_URL}/simple/notification",
            json={
                "email": "test@example.com",
                "message": "Hello from manual test!"
            }
        )
        print_response(response)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Server not running. Start it with: python 06_background_tasks_basic.py")
        return
    
    time.sleep(1)
    
    # Test 2: Async notification
    print("\n🧪 Test 2: Async Notification")
    response = requests.post(
        f"{BASIC_API_URL}/simple/notification-async",
        json={
            "email": "async@example.com",
            "message": "Async test message"
        }
    )
    print_response(response)
    
    time.sleep(1)
    
    # Test 3: Create order (multiple background tasks)
    print("\n🧪 Test 3: Create Order (Multiple Tasks)")
    response = requests.post(
        f"{BASIC_API_URL}/order",
        json={
            "item": "Gaming Console",
            "quantity": 2,
            "email": "gamer@example.com"
        }
    )
    print_response(response)
    
    time.sleep(1)
    
    # Test 4: Create async order
    print("\n🧪 Test 4: Create Async Order")
    response = requests.post(
        f"{BASIC_API_URL}/order-async",
        json={
            "item": "Smartwatch",
            "quantity": 1,
            "email": "tech@example.com"
        }
    )
    print_response(response)
    
    # Wait for background tasks to complete
    print("\n⏳ Waiting for background tasks to complete (8 seconds)...")
    time.sleep(8)
    
    # Test 5: Get logs
    print("\n🧪 Test 5: Get Logs")
    response = requests.get(f"{BASIC_API_URL}/logs")
    print_response(response)
    
    # Test 6: Clear logs
    print("\n🧪 Test 6: Clear Logs")
    response = requests.delete(f"{BASIC_API_URL}/logs")
    print_response(response)

def test_email_api():
    """Test email sending API"""
    print_section("Testing Email Sending API")
    
    # Test 1: Register user
    print("\n🧪 Test 1: User Registration")
    try:
        response = requests.post(
            f"{EMAIL_API_URL}/register",
            json={
                "username": "john_doe",
                "email": "john@example.com",
                "full_name": "John Doe"
            }
        )
        print_response(response)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Email server not running. Start it with: python 06_email_sending.py")
        return
    
    time.sleep(2)
    
    # Test 2: Register another user
    print("\n🧪 Test 2: Register Another User")
    response = requests.post(
        f"{EMAIL_API_URL}/register",
        json={
            "username": "jane_smith",
            "email": "jane@example.com",
            "full_name": "Jane Smith"
        }
    )
    print_response(response)
    
    time.sleep(2)
    
    # Test 3: Password reset
    print("\n🧪 Test 3: Password Reset Request")
    response = requests.post(
        f"{EMAIL_API_URL}/password-reset",
        json={
            "email": "john@example.com"
        }
    )
    print_response(response)
    
    time.sleep(2)
    
    # Test 4: Order confirmation
    print("\n🧪 Test 4: Order Confirmation Email")
    response = requests.post(
        f"{EMAIL_API_URL}/order-confirmation",
        json={
            "order_id": "ORD-12345",
            "email": "john@example.com",
            "items": ["Laptop", "Mouse", "Keyboard"],
            "total": 1299.99
        }
    )
    print_response(response)
    
    time.sleep(2)
    
    # Test 5: Newsletter subscription
    print("\n🧪 Test 5: Newsletter Subscription")
    response = requests.post(
        f"{EMAIL_API_URL}/subscribe-newsletter",
        json={
            "email": "jane@example.com",
            "preferences": ["Tech News", "Product Updates"]
        }
    )
    print_response(response)
    
    time.sleep(2)
    
    # Test 6: Bulk email
    print("\n🧪 Test 6: Bulk Email")
    response = requests.post(
        f"{EMAIL_API_URL}/bulk-email",
        json={
            "recipients": [
                "user1@example.com",
                "user2@example.com",
                "user3@example.com"
            ],
            "subject": "Important Announcement",
            "body": "This is a test bulk email message."
        }
    )
    print_response(response)
    
    # Wait for background tasks
    print("\n⏳ Waiting for background tasks to complete (8 seconds)...")
    time.sleep(8)
    
    # Test 7: Get email logs
    print("\n🧪 Test 7: Get All Email Logs")
    response = requests.get(f"{EMAIL_API_URL}/email-logs")
    print_response(response)
    
    # Test 8: Get user-specific logs
    print("\n🧪 Test 8: Get John's Email Logs")
    response = requests.get(f"{EMAIL_API_URL}/email-logs/john@example.com")
    print_response(response)
    
    # Test 9: List users
    print("\n🧪 Test 9: List All Users")
    response = requests.get(f"{EMAIL_API_URL}/users")
    print_response(response)

def test_validation():
    """Test input validation"""
    print_section("Testing Input Validation")
    
    # Test 1: Invalid email
    print("\n🧪 Test 1: Invalid Email Format")
    response = requests.post(
        f"{BASIC_API_URL}/simple/notification",
        json={
            "email": "not-an-email",
            "message": "Test"
        }
    )
    print_response(response)
    
    # Test 2: Missing fields
    print("\n🧪 Test 2: Missing Required Fields")
    response = requests.post(
        f"{BASIC_API_URL}/simple/notification",
        json={
            "email": "test@example.com"
        }
    )
    print_response(response)

def test_performance():
    """Test response time performance"""
    print_section("Testing Performance")
    
    print("\n🧪 Performance Test: Response Time with Background Tasks")
    print("Background task takes 3 seconds, but response should be instant\n")
    
    start = time.time()
    response = requests.post(
        f"{BASIC_API_URL}/simple/notification",
        json={
            "email": "perf@example.com",
            "message": "Performance test"
        }
    )
    duration = time.time() - start
    
    print(f"⏱️  Response Time: {duration:.3f} seconds")
    print(f"📊 Status Code: {response.status_code}")
    
    if duration < 1.0:
        print("✅ PASS: Response was fast (< 1 second)")
        print("   Background task will complete in ~3 seconds")
    else:
        print("❌ FAIL: Response was slow (>= 1 second)")

def main():
    """Main test runner"""
    print("\n" + "=" * 60)
    print("  🧪 FastAPI Background Tasks - Manual Test Suite")
    print("=" * 60)
    
    print("\nThis script will test both background tasks APIs.")
    print("Make sure the servers are running:")
    print("  Terminal 1: python 06_background_tasks_basic.py")
    print("  Terminal 2: python 06_email_sending.py")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled.")
        return
    
    # Run tests
    try:
        test_basic_api()
        
        print("\n" + "-" * 60)
        input("Press Enter to test Email API...")
        
        test_email_api()
        
        print("\n" + "-" * 60)
        input("Press Enter to test validation...")
        
        test_validation()
        
        print("\n" + "-" * 60)
        input("Press Enter to test performance...")
        
        test_performance()
        
        print_section("✅ All Tests Completed!")
        print("\n💡 Tips:")
        print("  • Check the server console for background task logs")
        print("  • Open http://localhost:8000/docs for interactive API docs")
        print("  • Open http://localhost:8001/docs for email API docs")
        print("  • Re-run this script anytime to test again")
        
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrupted by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
