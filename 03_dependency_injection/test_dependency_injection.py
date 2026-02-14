"""
Test script for the Dependency Injection API
Run the API first: python 03_dependency_injection.py
Then run this script: python test_dependency_injection.py
"""

import requests
import time
from typing import Dict

BASE_URL = "http://localhost:8000"
ADMIN_KEY = "admin_key_123"
USER_KEY = "user_key_456"

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"   {title}")
    print("="*70 + "\n")

def print_response(response: requests.Response, show_json: bool = True):
    """Print formatted response"""
    print(f"Status: {response.status_code} {response.reason}")
    if show_json:
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
    print()

# Test 1: Root endpoint
print_section("TEST 1: Root Endpoint (No Dependencies)")
response = requests.get(f"{BASE_URL}/")
print_response(response)

# Test 2: Create users
print_section("TEST 2: Create Users (Logging, Rate Limiting, Email Validation)")

users_to_create = [
    {
        "name": "John Doe",
        "email": "john@gmail.com",
        "age": 25,
        "password": "password123"
    },
    {
        "name": "Jane Smith",
        "email": "jane@outlook.com",
        "age": 30,
        "password": "secure456"
    },
    {
        "name": "Bob Wilson",
        "email": "bob@company.com",
        "age": 35,
        "password": "mypass789"
    }
]

for user in users_to_create:
    print(f"Creating user: {user['name']} ({user['email']})")
    response = requests.post(f"{BASE_URL}/users", json=user)
    print_response(response)
    time.sleep(0.5)  # Small delay between requests

# Test 3: Invalid email domain
print_section("TEST 3: Email Domain Validation (Should Fail)")
invalid_user = {
    "name": "Test User",
    "email": "test@invalid-domain.com",
    "age": 25,
    "password": "password123"
}
print("Attempting to create user with invalid email domain...")
response = requests.post(f"{BASE_URL}/users", json=invalid_user)
print_response(response)

# Test 4: List users without authentication
print_section("TEST 4: List Users Without Authentication (Should Fail)")
print("Attempting to list users without API key...")
response = requests.get(f"{BASE_URL}/users")
print_response(response)

# Test 5: List users with authentication
print_section("TEST 5: List Users With Authentication (User Key)")
print("Listing users with valid API key...")
response = requests.get(
    f"{BASE_URL}/users",
    headers={"api_key": USER_KEY}
)
print_response(response)

# Test 6: Get specific user
print_section("TEST 6: Get Specific User (Authenticated)")
print("Getting user with ID 1...")
response = requests.get(
    f"{BASE_URL}/users/1",
    headers={"api_key": USER_KEY}
)
print_response(response)

# Test 7: Update user without admin (should fail)
print_section("TEST 7: Update User Without Admin (Should Fail)")
print("Attempting to update user with regular user key...")
response = requests.put(
    f"{BASE_URL}/users/1",
    headers={"api_key": USER_KEY},
    json={"name": "Updated Name"}
)
print_response(response)

# Test 8: Update user with admin
print_section("TEST 8: Update User With Admin Key")
print("Updating user with admin key...")
response = requests.put(
    f"{BASE_URL}/users/1",
    headers={"api_key": ADMIN_KEY},
    json={"name": "John Updated", "age": 26}
)
print_response(response)

# Test 9: Rate limiting check
print_section("TEST 9: Check Rate Limit Status")
response = requests.get(f"{BASE_URL}/rate-limit-status")
print_response(response)

# Test 10: Trigger rate limit
print_section("TEST 10: Trigger Rate Limit (11 requests in quick succession)")
print("Making 11 rapid requests to trigger rate limit...")
for i in range(11):
    response = requests.get(f"{BASE_URL}/rate-limit-status")
    print(f"Request {i+1}: Status {response.status_code}")
    if response.status_code == 429:
        print("✅ Rate limit triggered!")
        print_response(response)
        break
    time.sleep(0.1)

# Test 11: API stats
print_section("TEST 11: Get API Statistics (Authenticated)")
response = requests.get(
    f"{BASE_URL}/stats",
    headers={"api_key": USER_KEY}
)
print_response(response)

# Test 12: Learning examples
print_section("TEST 12: Learning Examples")

print("1. Simple Dependency Example:")
response = requests.get(f"{BASE_URL}/learn/simple-dependency")
print_response(response)

print("2. Multiple Dependencies Example:")
response = requests.get(f"{BASE_URL}/learn/multiple-dependencies")
print_response(response)

print("3. Chained Dependencies Example (Admin only):")
response = requests.get(
    f"{BASE_URL}/learn/chained-dependencies",
    headers={"api_key": ADMIN_KEY}
)
print_response(response)

# Test 13: Delete user (admin only)
print_section("TEST 13: Delete User (Admin Only)")
print("Deleting user with ID 1...")
response = requests.delete(
    f"{BASE_URL}/users/1",
    headers={"api_key": ADMIN_KEY}
)
print(f"Status: {response.status_code} {response.reason}")
if response.status_code == 204:
    print("✅ User deleted successfully (No content returned)")
print()

# Verification
print_section("TEST 14: Verify User Deleted")
print("Attempting to get deleted user...")
response = requests.get(
    f"{BASE_URL}/users/1",
    headers={"api_key": USER_KEY}
)
print_response(response)

print_section("🎉 All Tests Complete!")
print("""
Key Takeaways:
1. ✅ Logging dependency tracks all requests
2. ✅ Rate limiting prevents abuse (10 req/min)
3. ✅ Email validation rejects invalid domains
4. ✅ Authentication required for sensitive endpoints
5. ✅ Authorization (admin) required for modifications
6. ✅ Database session managed automatically
7. ✅ Dependency chaining works (admin → user)
8. ✅ All dependencies run in order

Check the server logs to see the dependency execution!
""")
