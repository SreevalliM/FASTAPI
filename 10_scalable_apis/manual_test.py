"""
Manual Testing Script for Scalable APIs Module
==============================================

This script provides interactive testing of all examples
and helps you understand the concepts better.

Run with: python manual_test.py
"""

import httpx
import asyncio
import time
from typing import Dict, Any


# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"{text}")
    print(f"{'='*70}{Colors.END}\n")


def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def print_result(data: Dict[Any, Any], indent: int = 0):
    """Pretty print JSON data"""
    import json
    formatted = json.dumps(data, indent=2)
    for line in formatted.split('\n'):
        print(' ' * indent + line)


# ============================================================================
# Test Functions
# ============================================================================

async def test_async_basics():
    """Test async basics examples"""
    print_header("Testing Async Basics (Port 8000)")
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1: Root endpoint
            print_info("Test 1: Root endpoint")
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                print_success("Root endpoint working")
                print_result(response.json(), indent=2)
            else:
                print_error(f"Failed with status {response.status_code}")
            
            # Test 2: Sync vs Async comparison
            print_info("\nTest 2: Comparing sync vs async (5 requests)")
            start = time.time()
            response = await client.get(f"{base_url}/compare/sync-vs-async?requests=5")
            duration = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"Comparison complete in {duration:.2f}s")
                print(f"  Sync time:  {data['sync_time']}s")
                print(f"  Async time: {data['async_time']}s")
                print(f"  Speedup:    {data['speedup']}")
            
            # Test 3: Event loop demo
            print_info("\nTest 3: Event loop demonstration")
            response = await client.get(f"{base_url}/event-loop/demo")
            if response.status_code == 200:
                data = response.json()
                print_success("Event loop demo complete")
                print("  Execution log:")
                for log in data['execution_log']:
                    print(f"    - {log}")
            
            # Test 4: Concurrent dashboard
            print_info("\nTest 4: User dashboard (concurrent queries)")
            response = await client.get(f"{base_url}/async/user-dashboard/1")
            if response.status_code == 200:
                data = response.json()
                print_success(f"Dashboard loaded in {data['fetch_time']}s")
                print(f"  Note: {data['note']}")
    
    except httpx.ConnectError:
        print_error("Cannot connect to server on port 8000")
        print_info("Start the server with: python 10_async_basics.py")
    except Exception as e:
        print_error(f"Error: {str(e)}")


async def test_async_db_operations():
    """Test async database operations"""
    print_header("Testing Async DB Operations (Port 8001)")
    
    base_url = "http://localhost:8001"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1: Seed data
            print_info("Test 1: Seeding database")
            response = await client.post(f"{base_url}/seed-data")
            if response.status_code == 200:
                print_success("Database seeded")
            
            # Test 2: List users
            print_info("\nTest 2: Listing users")
            response = await client.get(f"{base_url}/users/")
            if response.status_code == 200:
                users = response.json()
                print_success(f"Found {len(users)} users")
                if users:
                    print("  First user:")
                    print_result(users[0], indent=4)
            
            # Test 3: Create product
            print_info("\nTest 3: Creating a product")
            product = {
                "name": "Test Product",
                "price": 99.99,
                "stock": 50
            }
            response = await client.post(f"{base_url}/products/", json=product)
            if response.status_code == 201:
                data = response.json()
                print_success(f"Product created with ID {data['id']}")
            
            # Test 4: Performance comparison
            print_info("\nTest 4: Sequential vs Concurrent queries")
            
            # Sequential
            start = time.time()
            response1 = await client.get(f"{base_url}/performance/blocking-queries")
            seq_time = time.time() - start
            
            # Concurrent
            start = time.time()
            response2 = await client.get(f"{base_url}/performance/concurrent-queries")
            conc_time = time.time() - start
            
            if response1.status_code == 200 and response2.status_code == 200:
                print_success("Performance comparison complete")
                print(f"  Sequential: {seq_time:.4f}s")
                print(f"  Concurrent: {conc_time:.4f}s")
                if conc_time < seq_time:
                    speedup = seq_time / conc_time
                    print(f"  Speedup: {speedup:.1f}x faster!")
    
    except httpx.ConnectError:
        print_error("Cannot connect to server on port 8001")
        print_info("Start the server with: python 10_async_db_operations.py")
    except Exception as e:
        print_error(f"Error: {str(e)}")


async def test_concurrency_patterns():
    """Test concurrency patterns"""
    print_header("Testing Concurrency Patterns (Port 8002)")
    
    base_url = "http://localhost:8002"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1: Parallel execution
            print_info("Test 1: Parallel execution with gather")
            response = await client.get(f"{base_url}/parallel/gather")
            if response.status_code == 200:
                data = response.json()
                print_success(f"Parallel execution complete in {data['total_time']}s")
                print(f"  Speedup: {data['speedup']}")
            
            # Test 2: Error handling
            print_info("\nTest 2: Error handling with return_exceptions")
            response = await client.get(f"{base_url}/error-handling/return-exceptions")
            if response.status_code == 200:
                data = response.json()
                print_success("Error handling test complete")
                results = data['results']
                success_count = sum(1 for r in results if r['status'] == 'success')
                failed_count = sum(1 for r in results if r['status'] == 'failed')
                print(f"  Successful: {success_count}")
                print(f"  Failed: {failed_count}")
            
            # Test 3: Timeout
            print_info("\nTest 3: Timeout handling")
            response = await client.get(f"{base_url}/timeout/basic")
            if response.status_code == 200:
                data = response.json()
                if 'error' in data:
                    print_success(f"Timeout triggered as expected: {data['error']}")
                else:
                    print_success("Operation completed within timeout")
            
            # Test 4: Rate limiting
            print_info("\nTest 4: Rate limiting with semaphore")
            print_info("This will take ~4 seconds (10 tasks, 3 concurrent)...")
            response = await client.get(f"{base_url}/rate-limiting/semaphore")
            if response.status_code == 200:
                data = response.json()
                print_success(f"Rate limiting test complete in {data['execution_time']}s")
                print(f"  Total tasks: {data['total_tasks']}")
                print(f"  Concurrent limit: {data['concurrent_limit']}")
            
            # Test 5: Background tasks
            print_info("\nTest 5: Background task management")
            task_id = f"test_{int(time.time())}"
            response = await client.post(f"{base_url}/tasks/create/{task_id}?duration=3")
            if response.status_code == 200:
                print_success(f"Background task '{task_id}' created")
                
                # Check status
                await asyncio.sleep(1)
                response = await client.get(f"{base_url}/tasks/status/{task_id}")
                if response.status_code == 200:
                    status = response.json()
                    print(f"  Status: {status['status']}")
            
            # Test 6: Data aggregation
            print_info("\nTest 6: Data aggregation from multiple sources")
            response = await client.get(f"{base_url}/aggregate/city-info/Chicago")
            if response.status_code == 200:
                data = response.json()
                print_success(f"Data aggregated in {data['fetch_time']}s")
                print(f"  Weather: {data['weather']}")
                print(f"  Traffic: {data['traffic']}")
    
    except httpx.ConnectError:
        print_error("Cannot connect to server on port 8002")
        print_info("Start the server with: python 10_concurrency_patterns.py")
    except Exception as e:
        print_error(f"Error: {str(e)}")


async def test_production_deployment():
    """Test production deployment features"""
    print_header("Testing Production Deployment (Port 8003)")
    
    base_url = "http://localhost:8003"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test 1: Basic health check
            print_info("Test 1: Basic health check")
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print_success(f"Health status: {data['status']}")
                print(f"  Version: {data['version']}")
            
            # Test 2: Detailed health check
            print_info("\nTest 2: Detailed health check")
            response = await client.get(f"{base_url}/health/detailed")
            if response.status_code == 200:
                data = response.json()
                print_success("Detailed health check passed")
                print("  System metrics:")
                print(f"    CPU: {data['system']['cpu_percent']:.1f}%")
                print(f"    Memory: {data['system']['memory_percent']:.1f}%")
                print(f"    Disk: {data['system']['disk_percent']:.1f}%")
            
            # Test 3: Readiness probe
            print_info("\nTest 3: Readiness probe")
            response = await client.get(f"{base_url}/health/ready")
            if response.status_code == 200:
                data = response.json()
                print_success(f"Readiness: {data['ready']}")
            
            # Test 4: Liveness probe
            print_info("\nTest 4: Liveness probe")
            response = await client.get(f"{base_url}/health/live")
            if response.status_code == 200:
                data = response.json()
                print_success(f"Liveness: {data['alive']}")
            
            # Test 5: Metrics
            print_info("\nTest 5: Metrics endpoint")
            response = await client.get(f"{base_url}/metrics")
            if response.status_code == 200:
                data = response.json()
                print_success("Metrics collected")
                print(f"  Process:")
                print(f"    PID: {data['process']['pid']}")
                print(f"    Memory: {data['process']['memory_mb']:.1f} MB")
                print(f"    CPU: {data['process']['cpu_percent']:.1f}%")
            
            # Test 6: Headers
            print_info("\nTest 6: Response headers")
            response = await client.get(f"{base_url}/")
            print_success("Headers checked")
            if 'x-process-time' in response.headers:
                print(f"  Process time: {response.headers['x-process-time']}")
            if 'x-request-id' in response.headers:
                print(f"  Request ID: {response.headers['x-request-id'][:16]}...")
    
    except httpx.ConnectError:
        print_error("Cannot connect to server on port 8003")
        print_info("Start the server with: python 10_production_deployment.py")
    except Exception as e:
        print_error(f"Error: {str(e)}")


async def run_all_tests():
    """Run all tests"""
    print_header("Manual Testing - Scalable APIs Module")
    print(f"{Colors.CYAN}This will test all four example applications.{Colors.END}")
    print(f"{Colors.CYAN}Make sure the servers are running on their respective ports.{Colors.END}\n")
    
    await test_async_basics()
    await asyncio.sleep(1)
    
    await test_async_db_operations()
    await asyncio.sleep(1)
    
    await test_concurrency_patterns()
    await asyncio.sleep(1)
    
    await test_production_deployment()
    
    print_header("Testing Complete!")
    print(f"{Colors.GREEN}All manual tests finished.{Colors.END}")
    print(f"\n{Colors.BLUE}To run automated tests, use:{Colors.END}")
    print(f"  pytest test_scalable_apis.py -v\n")


# ============================================================================
# Interactive Menu
# ============================================================================

def show_menu():
    """Show interactive menu"""
    print_header("Manual Testing Menu")
    print("Choose what to test:")
    print()
    print("  1. Async Basics (Port 8000)")
    print("  2. Async DB Operations (Port 8001)")
    print("  3. Concurrency Patterns (Port 8002)")
    print("  4. Production Deployment (Port 8003)")
    print("  5. Run ALL tests")
    print("  6. Exit")
    print()
    
    choice = input("Enter your choice (1-6): ").strip()
    return choice


async def main():
    """Main function"""
    while True:
        choice = show_menu()
        
        if choice == '1':
            await test_async_basics()
        elif choice == '2':
            await test_async_db_operations()
        elif choice == '3':
            await test_concurrency_patterns()
        elif choice == '4':
            await test_production_deployment()
        elif choice == '5':
            await run_all_tests()
        elif choice == '6':
            print_info("Goodbye! 👋")
            break
        else:
            print_error("Invalid choice. Please try again.")
        
        if choice != '6':
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrupted by user. Exiting...{Colors.END}\n")
