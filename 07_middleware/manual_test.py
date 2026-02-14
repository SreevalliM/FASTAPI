"""
Manual testing script for middleware examples.

Run this script to interactively test all middleware functionality.
"""

import requests
import time
from typing import Dict
import sys


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_response(response: requests.Response):
    """Print formatted response."""
    print(f"\n📤 Status: {response.status_code}")
    print(f"⏱️  Time: {response.elapsed.total_seconds():.4f}s")
    print("\n📋 Headers:")
    for key, value in response.headers.items():
        if key.lower().startswith('x-') or 'access-control' in key.lower():
            print(f"  {key}: {value}")
    print("\n📦 Body:")
    try:
        print(f"  {response.json()}")
    except:
        print(f"  {response.text[:200]}")


def test_basic_middleware(base_url: str = "http://localhost:8000"):
    """Test basic middleware endpoints."""
    print_header("Testing Basic Middleware")
    
    print("\n1️⃣ Testing Fast Endpoint")
    response = requests.get(f"{base_url}/fast")
    print_response(response)
    
    print("\n2️⃣ Testing Slow Endpoint (will take 2 seconds)")
    response = requests.get(f"{base_url}/slow")
    print_response(response)
    
    print("\n3️⃣ Testing POST with Data")
    response = requests.post(
        f"{base_url}/data",
        json={"test": "data", "number": 42}
    )
    print_response(response)
    
    print("\n4️⃣ Testing Large Response (GZip compression)")
    response = requests.get(f"{base_url}/large-response")
    print_response(response)
    print(f"  Response size: {len(response.content)} bytes")


def test_logging_middleware(base_url: str = "http://localhost:8001"):
    """Test logging middleware endpoints."""
    print_header("Testing Logging Middleware")
    
    print("\n1️⃣ Testing Request ID Generation")
    response1 = requests.get(f"{base_url}/")
    response2 = requests.get(f"{base_url}/")
    print_response(response1)
    print(f"\n🔍 Request IDs are unique:")
    print(f"  Request 1: {response1.headers.get('X-Request-ID')}")
    print(f"  Request 2: {response2.headers.get('X-Request-ID')}")
    
    print("\n2️⃣ Testing Item Endpoint")
    response = requests.get(f"{base_url}/test/123")
    print_response(response)
    
    print("\n3️⃣ Testing Login (Sensitive Data Filtering)")
    response = requests.post(
        f"{base_url}/login",
        json={"username": "testuser", "password": "secret123"}
    )
    print_response(response)
    print("  ℹ️  Password should NOT appear in logs")
    
    print("\n4️⃣ Testing Error Handling")
    response = requests.get(f"{base_url}/error")
    print_response(response)
    
    print("\n5️⃣ Testing HTTP Error")
    response = requests.get(f"{base_url}/http-error")
    print_response(response)
    
    print("\n6️⃣ Testing Slow Query (Performance Warning)")
    response = requests.get(f"{base_url}/slow-query")
    print_response(response)


def test_timing_middleware(base_url: str = "http://localhost:8002"):
    """Test timing middleware endpoints."""
    print_header("Testing Timing Middleware")
    
    print("\n1️⃣ Testing Fast Endpoint")
    response = requests.get(f"{base_url}/fast")
    print_response(response)
    performance = response.headers.get('X-Performance', 'unknown')
    print(f"  Performance: {performance}")
    
    print("\n2️⃣ Testing Medium Endpoint")
    response = requests.get(f"{base_url}/medium")
    print_response(response)
    performance = response.headers.get('X-Performance', 'unknown')
    print(f"  Performance: {performance}")
    
    print("\n3️⃣ Testing Slow Endpoint")
    response = requests.get(f"{base_url}/slow")
    print_response(response)
    performance = response.headers.get('X-Performance', 'unknown')
    print(f"  Performance: {performance}")
    
    print("\n4️⃣ Testing CPU Intensive")
    response = requests.get(f"{base_url}/cpu-intensive")
    print_response(response)
    
    print("\n5️⃣ Testing Database Simulation")
    response = requests.get(f"{base_url}/database-simulation")
    print_response(response)
    
    print("\n6️⃣ Testing Timed Operations")
    response = requests.get(f"{base_url}/timed-operations")
    print_response(response)
    
    print("\n7️⃣ Making Multiple Requests for Statistics")
    for _ in range(5):
        requests.get(f"{base_url}/fast")
        requests.get(f"{base_url}/medium")
    
    print("\n8️⃣ Viewing Statistics")
    response = requests.get(f"{base_url}/statistics")
    print_response(response)


def test_cors_middleware(base_url: str = "http://localhost:8003"):
    """Test CORS middleware endpoints."""
    print_header("Testing CORS Middleware")
    
    print("\n1️⃣ Testing Simple GET (No Preflight)")
    response = requests.get(
        f"{base_url}/preflight/simple",
        headers={"Origin": "http://localhost:3000"}
    )
    print_response(response)
    
    print("\n2️⃣ Testing POST (Triggers Preflight)")
    # First, the preflight request
    print("  OPTIONS (Preflight):")
    preflight = requests.options(
        f"{base_url}/preflight/complex",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type"
        }
    )
    print_response(preflight)
    
    # Then, the actual request
    print("\n  POST (Actual Request):")
    response = requests.post(
        f"{base_url}/preflight/complex",
        json={"test": "data"},
        headers={"Origin": "http://localhost:3000"}
    )
    print_response(response)
    
    print("\n3️⃣ Testing PUT (Preflight Required)")
    response = requests.put(
        f"{base_url}/preflight/update/123",
        json={"name": "Updated"},
        headers={"Origin": "http://localhost:3000"}
    )
    print_response(response)
    
    print("\n4️⃣ Testing DELETE (Preflight Required)")
    response = requests.delete(
        f"{base_url}/preflight/delete/123",
        headers={"Origin": "http://localhost:3000"}
    )
    print_response(response)
    
    print("\n5️⃣ Testing Custom Header")
    response = requests.get(
        f"{base_url}/preflight/with-custom-header",
        headers={"Origin": "http://localhost:3000"}
    )
    print_response(response)
    
    print("\n6️⃣ Testing Different Origin (May Fail)")
    response = requests.get(
        f"{base_url}/preflight/simple",
        headers={"Origin": "http://unauthorized-origin.com"}
    )
    print_response(response)
    print("  ℹ️  Check if Access-Control-Allow-Origin matches the request")


def check_server(url: str, name: str) -> bool:
    """Check if server is running."""
    try:
        response = requests.get(url, timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    """Main test runner."""
    print("\n🚀 FastAPI Middleware Manual Testing Suite")
    print("=" * 60)
    
    servers = [
        ("Basic Middleware", "http://localhost:8000"),
        ("Logging Middleware", "http://localhost:8001"),
        ("Timing Middleware", "http://localhost:8002"),
        ("CORS Middleware", "http://localhost:8003"),
    ]
    
    print("\n🔍 Checking which servers are running...")
    running_servers = []
    
    for name, url in servers:
        if check_server(url, name):
            print(f"  ✅ {name} - {url}")
            running_servers.append((name, url))
        else:
            print(f"  ❌ {name} - {url} (not running)")
    
    if not running_servers:
        print("\n❌ No servers are running!")
        print("\nTo start servers:")
        print("  python 07_middleware_basic.py")
        print("  python 07_logging_middleware.py")
        print("  python 07_timing_middleware.py")
        print("  python 07_cors_middleware.py")
        return
    
    print("\n" + "=" * 60)
    print("Choose what to test:")
    print("  1 - Test Basic Middleware (port 8000)")
    print("  2 - Test Logging Middleware (port 8001)")
    print("  3 - Test Timing Middleware (port 8002)")
    print("  4 - Test CORS Middleware (port 8003)")
    print("  5 - Test All Running Servers")
    print("  0 - Exit")
    print("=" * 60)
    
    try:
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            return
        elif choice == "1":
            if check_server("http://localhost:8000", "Basic"):
                test_basic_middleware()
            else:
                print("❌ Server not running on port 8000")
        elif choice == "2":
            if check_server("http://localhost:8001", "Logging"):
                test_logging_middleware()
            else:
                print("❌ Server not running on port 8001")
        elif choice == "3":
            if check_server("http://localhost:8002", "Timing"):
                test_timing_middleware()
            else:
                print("❌ Server not running on port 8002")
        elif choice == "4":
            if check_server("http://localhost:8003", "CORS"):
                test_cors_middleware()
            else:
                print("❌ Server not running on port 8003")
        elif choice == "5":
            for name, url in running_servers:
                if "Basic" in name and check_server(url, name):
                    test_basic_middleware(url)
                elif "Logging" in name and check_server(url, name):
                    test_logging_middleware(url)
                elif "Timing" in name and check_server(url, name):
                    test_timing_middleware(url)
                elif "CORS" in name and check_server(url, name):
                    test_cors_middleware(url)
        else:
            print("❌ Invalid choice")
        
        print("\n" + "=" * 60)
        print("✅ Testing Complete!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n👋 Testing interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
