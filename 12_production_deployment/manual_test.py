"""
Manual API Testing Script
Test the production API endpoints manually
"""

import httpx
import asyncio
import json
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_test(name):
    """Print test name"""
    print(f"{Colors.CYAN}▶ {name}{Colors.END}")


def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}  ✓ {message}{Colors.END}")


def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}  ✗ {message}{Colors.END}")


def print_info(message):
    """Print info message"""
    print(f"{Colors.BLUE}  ℹ {message}{Colors.END}")


def print_response(response):
    """Print response details"""
    print(f"{Colors.YELLOW}  Status: {response.status_code}{Colors.END}")
    
    # Print headers of interest
    headers_to_show = ['x-request-id', 'x-process-time', 'content-type']
    for header in headers_to_show:
        if header in response.headers:
            print(f"{Colors.YELLOW}  {header}: {response.headers[header]}{Colors.END}")
    
    # Print response body
    try:
        data = response.json()
        print(f"{Colors.YELLOW}  Response: {json.dumps(data, indent=2)}{Colors.END}")
    except:
        print(f"{Colors.YELLOW}  Response: {response.text[:200]}{Colors.END}")


async def test_api(base_url="http://localhost:8000"):
    """Run all API tests"""
    
    print_header("FastAPI Production API - Manual Testing")
    print_info(f"Testing API at: {base_url}")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Root endpoint
        print_header("Test 1: Root Endpoint")
        print_test("GET /")
        try:
            response = await client.get(f"{base_url}/")
            print_response(response)
            if response.status_code == 200:
                print_success("Root endpoint is working")
            else:
                print_error(f"Unexpected status code: {response.status_code}")
        except Exception as e:
            print_error(f"Failed to connect: {e}")
            print_error("Make sure the server is running!")
            return
        
        # Test 2: Health check
        print_header("Test 2: Health Check")
        print_test("GET /health")
        try:
            response = await client.get(f"{base_url}/health")
            print_response(response)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print_success("Health check passed")
                else:
                    print_error("Health check returned unhealthy status")
            else:
                print_error(f"Health check failed with status: {response.status_code}")
        except Exception as e:
            print_error(f"Health check failed: {e}")
        
        # Test 3: Readiness check
        print_header("Test 3: Readiness Check")
        print_test("GET /ready")
        try:
            response = await client.get(f"{base_url}/ready")
            print_response(response)
            if response.status_code == 200:
                print_success("Readiness check passed")
            else:
                print_error(f"Readiness check failed with status: {response.status_code}")
        except Exception as e:
            print_error(f"Readiness check failed: {e}")
        
        # Test 4: Metrics endpoint
        print_header("Test 4: Metrics Endpoint")
        print_test("GET /metrics")
        try:
            response = await client.get(f"{base_url}/metrics")
            print_response(response)
            if response.status_code == 200:
                print_success("Metrics endpoint is working")
            else:
                print_error(f"Metrics endpoint failed with status: {response.status_code}")
        except Exception as e:
            print_error(f"Metrics endpoint failed: {e}")
        
        # Test 5: Create item
        print_header("Test 5: Create Item")
        print_test("POST /items")
        item_data = {
            "name": "Test Product",
            "description": "A test product for manual testing",
            "price": 49.99
        }
        print_info(f"Request body: {json.dumps(item_data, indent=2)}")
        try:
            response = await client.post(f"{base_url}/items", json=item_data)
            print_response(response)
            if response.status_code == 201:
                item = response.json()
                item_id = item.get("id")
                print_success(f"Item created successfully with ID: {item_id}")
            else:
                print_error(f"Failed to create item with status: {response.status_code}")
                item_id = None
        except Exception as e:
            print_error(f"Failed to create item: {e}")
            item_id = None
        
        # Test 6: List items
        print_header("Test 6: List Items")
        print_test("GET /items")
        try:
            response = await client.get(f"{base_url}/items")
            print_response(response)
            if response.status_code == 200:
                items = response.json()
                print_success(f"Retrieved {len(items)} items")
            else:
                print_error(f"Failed to list items with status: {response.status_code}")
        except Exception as e:
            print_error(f"Failed to list items: {e}")
        
        # Test 7: Get specific item
        if item_id:
            print_header("Test 7: Get Specific Item")
            print_test(f"GET /items/{item_id}")
            try:
                response = await client.get(f"{base_url}/items/{item_id}")
                print_response(response)
                if response.status_code == 200:
                    print_success("Item retrieved successfully")
                else:
                    print_error(f"Failed to get item with status: {response.status_code}")
            except Exception as e:
                print_error(f"Failed to get item: {e}")
        
        # Test 8: Get non-existent item
        print_header("Test 8: Get Non-Existent Item")
        print_test("GET /items/nonexistent-id")
        try:
            response = await client.get(f"{base_url}/items/nonexistent-id")
            print_response(response)
            if response.status_code == 404:
                print_success("Correctly returned 404 for non-existent item")
            else:
                print_error(f"Unexpected status code: {response.status_code}")
        except Exception as e:
            print_error(f"Failed to test non-existent item: {e}")
        
        # Test 9: Invalid item creation
        print_header("Test 9: Invalid Item Creation")
        print_test("POST /items (with invalid data)")
        invalid_data = {
            "name": "",  # Empty name
            "price": -10  # Negative price
        }
        print_info(f"Request body: {json.dumps(invalid_data, indent=2)}")
        try:
            response = await client.post(f"{base_url}/items", json=invalid_data)
            print_response(response)
            if response.status_code == 422:
                print_success("Correctly validated and rejected invalid data")
            else:
                print_error(f"Unexpected status code: {response.status_code}")
        except Exception as e:
            print_error(f"Failed to test validation: {e}")
        
        # Test 10: Delete item
        if item_id:
            print_header("Test 10: Delete Item")
            print_test(f"DELETE /items/{item_id}")
            try:
                response = await client.delete(f"{base_url}/items/{item_id}")
                print_response(response)
                if response.status_code == 204:
                    print_success("Item deleted successfully")
                    
                    # Verify deletion
                    print_test(f"Verifying deletion: GET /items/{item_id}")
                    verify_response = await client.get(f"{base_url}/items/{item_id}")
                    if verify_response.status_code == 404:
                        print_success("Verified item was deleted")
                    else:
                        print_error("Item still exists after deletion")
                else:
                    print_error(f"Failed to delete item with status: {response.status_code}")
            except Exception as e:
                print_error(f"Failed to delete item: {e}")
        
        # Test 11: Request ID tracking
        print_header("Test 11: Request ID Tracking")
        print_test("Testing request ID in headers")
        try:
            response1 = await client.get(f"{base_url}/")
            response2 = await client.get(f"{base_url}/")
            
            request_id_1 = response1.headers.get('x-request-id')
            request_id_2 = response2.headers.get('x-request-id')
            
            if request_id_1 and request_id_2:
                print_success(f"Request ID 1: {request_id_1}")
                print_success(f"Request ID 2: {request_id_2}")
                if request_id_1 != request_id_2:
                    print_success("Request IDs are unique")
                else:
                    print_error("Request IDs are not unique")
            else:
                print_error("Request ID header missing")
        except Exception as e:
            print_error(f"Failed to test request IDs: {e}")
        
        # Test 12: API documentation (if enabled)
        print_header("Test 12: API Documentation")
        print_test("GET /api/docs")
        try:
            response = await client.get(f"{base_url}/api/docs")
            if response.status_code == 200:
                print_success("API documentation is accessible")
                print_info("Visit http://localhost:8000/api/docs in your browser")
            elif response.status_code == 404:
                print_info("API documentation is disabled (expected in production)")
            else:
                print_error(f"Unexpected status code: {response.status_code}")
        except Exception as e:
            print_error(f"Failed to test documentation: {e}")
    
    # Summary
    print_header("Test Summary")
    print_info(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info("All manual tests completed!")
    print_info("\nFor automated testing, run: pytest test_production_api.py -v")


def main():
    """Main function"""
    import sys
    
    # Get base URL from command line argument or use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"{Colors.BOLD}FastAPI Production API Testing{Colors.END}")
    print(f"Target: {base_url}\n")
    
    # Run async tests
    asyncio.run(test_api(base_url))


if __name__ == "__main__":
    main()
