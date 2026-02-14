"""
Manual Testing Script for Architecture Mastery Module

Tests all the various architecture patterns with real HTTP requests.
"""

import httpx
import asyncio
import json
import time
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60 + "\n")


def print_result(test_name: str, response: httpx.Response):
    """Print test result"""
    status_icon = "✓" if response.status_code < 400 else "✗"
    print(f"{status_icon} {test_name}")
    print(f"   Status: {response.status_code}")
    if response.text:
        try:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)[:200]}")
        except:
            print(f"   Response: {response.text[:200]}")
    print()


async def test_clean_architecture():
    """Test clean architecture endpoints"""
    print_section("Testing Clean Architecture")
    
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Root endpoint
        response = await client.get("/")
        print_result("GET /", response)
        
        # Create product
        product_data = {
            "name": "Test Laptop",
            "price": 999.99,
            "stock": 10
        }
        response = await client.post("/products", json=product_data)
        print_result("POST /products", response)
        
        if response.status_code == 201:
            product = response.json()
            product_id = product["id"]
            
            # Get product
            response = await client.get(f"/products/{product_id}")
            print_result(f"GET /products/{product_id}", response)
            
            # Update price
            response = await client.patch(
                f"/products/{product_id}/price",
                json={"price": 899.99}
            )
            print_result(f"PATCH /products/{product_id}/price", response)
            
            # Create order
            order_data = {
                "customer_email": "test@example.com",
                "items": [
                    {"product_id": product_id, "quantity": 2}
                ]
            }
            response = await client.post("/orders", json=order_data)
            print_result("POST /orders", response)


async def test_repository_pattern():
    """Test repository pattern"""
    print_section("Testing Repository Pattern")
    
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Create user
        user_data = {
            "email": "alice@example.com",
            "username": "alice",
            "full_name": "Alice Smith",
            "is_active": True
        }
        response = await client.post("/users", json=user_data)
        print_result("POST /users", response)
        
        if response.status_code == 201:
            user = response.json()
            user_id = user["id"]
            
            # Get user (should be cached on second call)
            start = time.time()
            response1 = await client.get(f"/users/{user_id}")
            time1 = time.time() - start
            
            start = time.time()
            response2 = await client.get(f"/users/{user_id}")
            time2 = time.time() - start
            
            print(f"First request: {time1*1000:.2f}ms")
            print(f"Second request: {time2*1000:.2f}ms (cached)")
            print_result(f"GET /users/{user_id}", response2)
            
            # Get stats
            response = await client.get("/stats")
            print_result("GET /stats", response)


async def test_rate_limiting():
    """Test rate limiting"""
    print_section("Testing Rate Limiting")
    
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Test basic rate limit (5 per minute)
        print("Testing basic rate limit (5/minute)...")
        success_count = 0
        rate_limited = False
        
        for i in range(7):
            try:
                response = await client.get("/slowapi/basic")
                if response.status_code == 200:
                    success_count += 1
                    print(f"  Request {i+1}: ✓ Success")
                elif response.status_code == 429:
                    rate_limited = True
                    print(f"  Request {i+1}: ✗ Rate limited")
            except Exception as e:
                print(f"  Request {i+1}: ✗ Error: {e}")
            
            await asyncio.sleep(0.1)
        
        print(f"\nSuccessful requests: {success_count}")
        print(f"Rate limiting working: {'✓ Yes' if rate_limited else '✗ No'}")
        
        # Test token bucket
        response = await client.get("/token-bucket/data")
        print_result("GET /token-bucket/data", response)
        
        # Get stats
        response = await client.get("/stats")
        print_result("GET /stats", response)


async def test_caching():
    """Test Redis caching"""
    print_section("Testing Redis Caching")
    
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Get cache stats
        response = await client.get("/cache/stats")
        print_result("GET /cache/stats", response)
        
        # Create product
        product_data = {
            "id": 0,
            "name": "Cached Product",
            "description": "Test product for caching",
            "price": 49.99,
            "category": "Test",
            "stock": 100
        }
        response = await client.post("/products", json=product_data)
        print_result("POST /products", response)
        
        if response.status_code == 201:
            product_id = response.json()["product"]["id"]
            
            # First request (cache miss)
            start = time.time()
            response1 = await client.get(f"/products/{product_id}")
            time1 = time.time() - start
            
            # Second request (cache hit)
            start = time.time()
            response2 = await client.get(f"/products/{product_id}")
            time2 = time.time() - start
            
            print(f"Cache miss: {time1*1000:.2f}ms")
            print(f"Cache hit: {time2*1000:.2f}ms")
            print(f"Speed improvement: {(time1/time2):.1f}x faster")
            
            # Get updated stats
            response = await client.get("/cache/stats")
            print_result("GET /cache/stats (after)", response)


async def test_api_gateway():
    """Test API Gateway"""
    print_section("Testing API Gateway")
    
    # Note: Requires backend services to be running
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Test without API key (should fail)
        response = await client.get("/api/users")
        print_result("GET /api/users (no auth)", response)
        
        # Test with API key
        headers = {"X-API-Key": "user_key_123"}
        response = await client.get("/api/users", headers=headers)
        print_result("GET /api/users (with auth)", response)
        
        # Test health check
        response = await client.get("/health")
        print_result("GET /health", response)
        
        # Test aggregated endpoint
        response = await client.get("/api/dashboard", headers=headers)
        print_result("GET /api/dashboard", response)


def test_microservices():
    """Test microservices (requires all services running)"""
    print_section("Testing Microservices")
    
    print("To test microservices, run each service in a separate terminal:")
    print("  python 13_microservices_example.py users")
    print("  python 13_microservices_example.py products")
    print("  python 13_microservices_example.py orders")
    print("  python 13_microservices_example.py message_bus")
    print("\nThen test with:")
    print("  curl http://localhost:8001/users")
    print("  curl http://localhost:8002/products")
    print("  curl http://localhost:8003/orders")
    print("  curl http://localhost:8004/events")


async def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print(" ARCHITECTURE MASTERY - MANUAL TESTS")
    print("=" * 60)
    
    print("\nNote: Make sure the appropriate service is running on port 8000")
    print("Change to the service you want to test before running.\n")
    
    tests = [
        ("Clean Architecture", test_clean_architecture),
        ("Repository Pattern", test_repository_pattern),
        ("Rate Limiting", test_rate_limiting),
        ("Redis Caching", test_caching),
        ("API Gateway", test_api_gateway),
    ]
    
    for name, test_func in tests:
        try:
            await test_func()
        except Exception as e:
            print(f"\n✗ Error testing {name}: {e}\n")
    
    # Microservices (no async)
    test_microservices()
    
    print("\n" + "=" * 60)
    print(" ALL TESTS COMPLETED")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    print("Manual Testing Script")
    print("\nChoose what to test:")
    print("1. Clean Architecture (port 8000)")
    print("2. Repository Pattern (port 8000)")
    print("3. Rate Limiting (port 8000)")
    print("4. Redis Caching (port 8000)")
    print("5. API Gateway (port 8000)")
    print("6. Microservices (ports 8001-8004)")
    print("7. Run all tests")
    
    choice = input("\nEnter choice (1-7): ").strip()
    
    test_map = {
        "1": test_clean_architecture,
        "2": test_repository_pattern,
        "3": test_rate_limiting,
        "4": test_caching,
        "5": test_api_gateway,
        "6": test_microservices,
        "7": run_all_tests
    }
    
    if choice == "6":
        test_microservices()
    elif choice in test_map:
        asyncio.run(test_map[choice]())
    else:
        print("Invalid choice")
