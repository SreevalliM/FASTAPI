"""
🧪 Manual Authentication Testing Script
=========================================
Test the authentication API manually without pytest.

Usage:
    python manual_test.py

Make sure the API is running first:
    uvicorn 05_user_auth_api:app --reload
"""

import requests
import json
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_section(title: str):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_response(response: requests.Response):
    """Print formatted response"""
    print(f"{Colors.MAGENTA}Status Code: {response.status_code}{Colors.RESET}")
    try:
        print(f"{Colors.MAGENTA}Response: {json.dumps(response.json(), indent=2)}{Colors.RESET}")
    except:
        print(f"{Colors.MAGENTA}Response: {response.text}{Colors.RESET}")

def test_connection():
    """Test if API is running"""
    print_section("🔌 Testing Connection")
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=2)
        if response.status_code == 200:
            print_success("API is running!")
            print_response(response)
            return True
        else:
            print_error("API returned unexpected status")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Make sure it's running:")
        print_info("uvicorn 05_user_auth_api:app --reload")
        return False

def test_public_endpoint():
    """Test public endpoint (no auth required)"""
    print_section("🌐 Testing Public Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/")
        print_response(response)
        if response.status_code == 200:
            print_success("Public endpoint accessible")
            return True
        else:
            print_error("Failed to access public endpoint")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_login(username: str, password: str) -> Optional[str]:
    """Test login and return token"""
    print_section(f"🔑 Testing Login - {username}")
    try:
        response = requests.post(
            f"{BASE_URL}/token",
            data={"username": username, "password": password}
        )
        print_response(response)
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print_success(f"Login successful! Token received")
            print_info(f"Token preview: {token[:50]}...")
            return token
        else:
            print_error("Login failed")
            return None
    except Exception as e:
        print_error(f"Error: {e}")
        return None

def test_protected_endpoint_without_auth():
    """Test accessing protected endpoint without authentication"""
    print_section("🚫 Testing Protected Endpoint WITHOUT Token")
    try:
        response = requests.get(f"{BASE_URL}/users/me")
        print_response(response)
        
        if response.status_code == 401:
            print_success("Correctly blocked - authentication required")
            return True
        else:
            print_warning("Expected 401 but got different status")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_protected_endpoint_with_auth(token: str, username: str):
    """Test accessing protected endpoint with authentication"""
    print_section(f"✅ Testing Protected Endpoint WITH Token - {username}")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Authenticated as: {data['username']}")
            print_info(f"Role: {data['role']}")
            print_info(f"Email: {data['email']}")
            return True
        else:
            print_error("Failed to access protected endpoint")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_admin_endpoint(token: str, username: str):
    """Test admin-only endpoint"""
    print_section(f"👑 Testing Admin Endpoint - {username}")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/users", headers=headers)
        print_response(response)
        
        if response.status_code == 200:
            users = response.json()
            print_success(f"Access granted! Found {len(users)} users")
            return True
        elif response.status_code == 403:
            print_warning("Access denied - Admin role required")
            return False
        else:
            print_error("Unexpected response")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_scoped_endpoint(token: str, username: str, scope: str):
    """Test endpoint with security scopes"""
    print_section(f"🔐 Testing Scoped Endpoint ({scope}) - {username}")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        if scope == "items:read":
            response = requests.get(f"{BASE_URL}/users/me/items", headers=headers)
        elif scope == "items:write":
            response = requests.post(f"{BASE_URL}/items?title=Test", headers=headers)
        else:
            print_error(f"Unknown scope: {scope}")
            return False
        
        print_response(response)
        
        if response.status_code == 200:
            print_success(f"Access granted with {scope} scope")
            return True
        elif response.status_code == 403:
            print_warning(f"Access denied - {scope} scope required")
            return False
        else:
            print_error("Unexpected response")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_registration():
    """Test user registration"""
    print_section("📝 Testing User Registration")
    try:
        new_user = {
            "username": "testuser_manual",
            "email": "testuser@example.com",
            "full_name": "Test User",
            "password": "TestPass123",
            "role": "user"
        }
        
        response = requests.post(f"{BASE_URL}/register", json=new_user)
        print_response(response)
        
        if response.status_code == 201:
            print_success("User registered successfully")
            return True
        elif response.status_code == 400:
            print_warning("User might already exist (this is okay)")
            return True
        else:
            print_error("Registration failed")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def run_all_tests():
    """Run all manual tests"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     🔐 OAuth2 + JWT Authentication Manual Testing 🔐      ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    # Test connection
    if not test_connection():
        return
    
    # Test public endpoints
    test_public_endpoint()
    
    # Test protected endpoint without auth
    test_protected_endpoint_without_auth()
    
    # Test login and subsequent requests for different users
    print_info("Testing with Admin user (alice)...")
    alice_token = test_login("alice", "secret")
    if alice_token:
        test_protected_endpoint_with_auth(alice_token, "alice")
        test_admin_endpoint(alice_token, "alice")
        test_scoped_endpoint(alice_token, "alice", "items:read")
        test_scoped_endpoint(alice_token, "alice", "items:write")
    
    print_info("\nTesting with Regular user (bob)...")
    bob_token = test_login("bob", "secret")
    if bob_token:
        test_protected_endpoint_with_auth(bob_token, "bob")
        test_admin_endpoint(bob_token, "bob")  # Should fail
        test_scoped_endpoint(bob_token, "bob", "items:read")
        test_scoped_endpoint(bob_token, "bob", "items:write")  # Should fail
    
    # Test registration
    test_registration()
    
    # Test invalid credentials
    print_section("❌ Testing Invalid Credentials")
    test_login("invalid", "wrong")
    
    # Summary
    print_section("📊 Testing Complete!")
    print_success("All manual tests completed")
    print_info("Check the results above for any failures")
    print_info("For automated testing, use: pytest test_authentication.py -v")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Testing interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.RESET}")
