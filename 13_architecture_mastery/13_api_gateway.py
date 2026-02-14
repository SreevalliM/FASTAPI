"""
API Gateway Pattern with FastAPI

An API Gateway is a single entry point for multiple microservices.
It handles:
- Request routing
- Authentication & Authorization
- Rate limiting
- Request/Response transformation
- Load balancing
- Circuit breaking
- Service discovery
- Logging & Monitoring

Run: uvicorn 13_api_gateway:app --reload --port 8000

Then run backend services:
    uvicorn 13_api_gateway:users_service --reload --port 8001
    uvicorn 13_api_gateway:products_service --reload --port 8002
    uvicorn 13_api_gateway:orders_service --reload --port 8003
"""

from fastapi import FastAPI, HTTPException, Header, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import httpx
import asyncio
import time
from enum import Enum


# ====================================
# CONFIGURATION
# ====================================

class ServiceConfig:
    """Configuration for backend services"""
    USERS_SERVICE = "http://localhost:8001"
    PRODUCTS_SERVICE = "http://localhost:8002"
    ORDERS_SERVICE = "http://localhost:8003"
    
    # Circuit breaker settings
    FAILURE_THRESHOLD = 5
    TIMEOUT_SECONDS = 30
    REQUEST_TIMEOUT = 5.0


# ====================================
# CIRCUIT BREAKER PATTERN
# ====================================

class CircuitState(str, Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failures exceeded, block requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit Breaker pattern to prevent cascading failures
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 30
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
    
    def record_success(self):
        """Record successful request"""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
    
    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def can_attempt(self) -> bool:
        """Check if request can be attempted"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if timeout has elapsed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed >= self.timeout_seconds:
                    self.state = CircuitState.HALF_OPEN
                    return True
            return False
        
        # HALF_OPEN: allow one request to test
        return True
    
    def get_status(self) -> Dict:
        """Get circuit breaker status"""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None
        }


# ====================================
# SERVICE REGISTRY & DISCOVERY
# ====================================

class ServiceRegistry:
    """
    Simple service registry for service discovery
    In production, use Consul, Eureka, or Kubernetes DNS
    """
    
    def __init__(self):
        self.services: Dict[str, List[str]] = {
            "users": ["http://localhost:8001"],
            "products": ["http://localhost:8002"],
            "orders": ["http://localhost:8003"]
        }
        self.current_index: Dict[str, int] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def register_service(self, name: str, url: str):
        """Register a service"""
        if name not in self.services:
            self.services[name] = []
        if url not in self.services[name]:
            self.services[name].append(url)
    
    def get_service_url(self, name: str) -> Optional[str]:
        """Get service URL with round-robin load balancing"""
        if name not in self.services or not self.services[name]:
            return None
        
        # Round-robin load balancing
        if name not in self.current_index:
            self.current_index[name] = 0
        
        urls = self.services[name]
        url = urls[self.current_index[name]]
        self.current_index[name] = (self.current_index[name] + 1) % len(urls)
        
        return url
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(
                failure_threshold=ServiceConfig.FAILURE_THRESHOLD,
                timeout_seconds=ServiceConfig.TIMEOUT_SECONDS
            )
        return self.circuit_breakers[service_name]
    
    def get_all_services(self) -> Dict:
        """Get all registered services"""
        return {
            name: {
                "urls": urls,
                "circuit_breaker": self.get_circuit_breaker(name).get_status()
            }
            for name, urls in self.services.items()
        }


# ====================================
# API GATEWAY SERVICE
# ====================================

# Initialize service registry
service_registry = ServiceRegistry()

# HTTP client for backend requests
http_client: Optional[httpx.AsyncClient] = None


async def get_http_client() -> httpx.AsyncClient:
    """Get or create HTTP client"""
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(timeout=ServiceConfig.REQUEST_TIMEOUT)
    return http_client


class APIGateway:
    """
    API Gateway that routes requests to backend services
    """
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
    
    async def proxy_request(
        self,
        service_name: str,
        path: str,
        method: str = "GET",
        headers: Optional[Dict] = None,
        body: Optional[Dict] = None
    ) -> Dict:
        """
        Proxy request to backend service with circuit breaker
        """
        # Get circuit breaker
        circuit_breaker = self.registry.get_circuit_breaker(service_name)
        
        # Check circuit breaker
        if not circuit_breaker.can_attempt():
            raise HTTPException(
                status_code=503,
                detail=f"Service {service_name} is currently unavailable (circuit open)"
            )
        
        # Get service URL
        service_url = self.registry.get_service_url(service_name)
        if not service_url:
            raise HTTPException(
                status_code=503,
                detail=f"Service {service_name} not found"
            )
        
        # Build full URL
        full_url = f"{service_url}{path}"
        
        # Make request
        client = await get_http_client()
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = await client.get(full_url, headers=headers)
            elif method == "POST":
                response = await client.post(full_url, json=body, headers=headers)
            elif method == "PUT":
                response = await client.put(full_url, json=body, headers=headers)
            elif method == "DELETE":
                response = await client.delete(full_url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            elapsed = time.time() - start_time
            
            # Record success
            circuit_breaker.record_success()
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.text else {},
                "headers": dict(response.headers),
                "response_time_ms": round(elapsed * 1000, 2)
            }
            
        except (httpx.RequestError, httpx.TimeoutException) as e:
            # Record failure
            circuit_breaker.record_failure()
            
            raise HTTPException(
                status_code=503,
                detail=f"Service {service_name} unavailable: {str(e)}"
            )


# ====================================
# AUTHENTICATION & AUTHORIZATION
# ====================================

# Simple API key store (in production, use proper auth service)
API_KEYS = {
    "user_key_123": {"user_id": 1, "role": "user"},
    "admin_key_456": {"user_id": 2, "role": "admin"}
}


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> Dict:
    """Verify API key"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return API_KEYS[x_api_key]


# ====================================
# FASTAPI APPLICATION (API GATEWAY)
# ====================================

app = FastAPI(
    title="API Gateway",
    description="Single entry point for microservices",
    version="1.0.0"
)

gateway = APIGateway(service_registry)


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    if http_client:
        await http_client.aclose()


@app.get("/")
async def root():
    """Gateway information"""
    return {
        "message": "API Gateway",
        "services": service_registry.get_all_services(),
        "features": [
            "Request routing",
            "Circuit breaker",
            "Load balancing",
            "Authentication",
            "Rate limiting"
        ],
        "endpoints": {
            "users": "/api/users/*",
            "products": "/api/products/*",
            "orders": "/api/orders/*",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check for all services"""
    services_health = {}
    
    for service_name in ["users", "products", "orders"]:
        circuit_breaker = service_registry.get_circuit_breaker(service_name)
        services_health[service_name] = {
            "status": circuit_breaker.state,
            "healthy": circuit_breaker.state != CircuitState.OPEN
        }
    
    all_healthy = all(s["healthy"] for s in services_health.values())
    
    return {
        "gateway": "healthy",
        "services": services_health,
        "overall_status": "healthy" if all_healthy else "degraded"
    }


# ====================================
# USER SERVICE ROUTES
# ====================================

@app.get("/api/users")
async def list_users(auth: Dict = Depends(verify_api_key)):
    """List users (proxied to users service)"""
    result = await gateway.proxy_request("users", "/users", method="GET")
    return result["data"]


@app.get("/api/users/{user_id}")
async def get_user(user_id: int, auth: Dict = Depends(verify_api_key)):
    """Get user by ID (proxied to users service)"""
    result = await gateway.proxy_request("users", f"/users/{user_id}", method="GET")
    return result["data"]


@app.post("/api/users")
async def create_user(user_data: Dict, auth: Dict = Depends(verify_api_key)):
    """Create user (proxied to users service)"""
    if auth["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    result = await gateway.proxy_request("users", "/users", method="POST", body=user_data)
    return result["data"]


# ====================================
# PRODUCT SERVICE ROUTES
# ====================================

@app.get("/api/products")
async def list_products(auth: Dict = Depends(verify_api_key)):
    """List products (proxied to products service)"""
    result = await gateway.proxy_request("products", "/products", method="GET")
    return result["data"]


@app.get("/api/products/{product_id}")
async def get_product(product_id: int, auth: Dict = Depends(verify_api_key)):
    """Get product by ID (proxied to products service)"""
    result = await gateway.proxy_request("products", f"/products/{product_id}", method="GET")
    return result["data"]


# ====================================
# ORDER SERVICE ROUTES
# ====================================

@app.get("/api/orders")
async def list_orders(auth: Dict = Depends(verify_api_key)):
    """List orders (proxied to orders service)"""
    result = await gateway.proxy_request("orders", "/orders", method="GET")
    return result["data"]


@app.post("/api/orders")
async def create_order(order_data: Dict, auth: Dict = Depends(verify_api_key)):
    """Create order (proxied to orders service)"""
    result = await gateway.proxy_request("orders", "/orders", method="POST", body=order_data)
    return result["data"]


# ====================================
# AGGREGATED ENDPOINTS (Gateway-specific)
# ====================================

@app.get("/api/dashboard")
async def get_dashboard(auth: Dict = Depends(verify_api_key)):
    """
    Aggregated dashboard data from multiple services
    Demonstrates service composition
    """
    user_id = auth["user_id"]
    
    try:
        # Parallel requests to multiple services
        user_task = gateway.proxy_request("users", f"/users/{user_id}")
        orders_task = gateway.proxy_request("orders", f"/orders?user_id={user_id}")
        
        user_result, orders_result = await asyncio.gather(
            user_task,
            orders_task,
            return_exceptions=True
        )
        
        return {
            "user": user_result["data"] if not isinstance(user_result, Exception) else None,
            "orders": orders_result["data"] if not isinstance(orders_result, Exception) else None,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================================
# BACKEND SERVICES (For Demo)
# ====================================

# Users Service
users_service = FastAPI(title="Users Service")

@users_service.get("/users")
async def users_list():
    return [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"}
    ]

@users_service.get("/users/{user_id}")
async def users_get(user_id: int):
    return {"id": user_id, "name": f"User {user_id}", "email": f"user{user_id}@example.com"}

@users_service.post("/users")
async def users_create(user_data: Dict):
    return {"id": 3, **user_data}


# Products Service
products_service = FastAPI(title="Products Service")

@products_service.get("/products")
async def products_list():
    return [
        {"id": 1, "name": "Laptop", "price": 999.99},
        {"id": 2, "name": "Mouse", "price": 29.99}
    ]

@products_service.get("/products/{product_id}")
async def products_get(product_id: int):
    return {"id": product_id, "name": f"Product {product_id}", "price": 99.99}


# Orders Service
orders_service = FastAPI(title="Orders Service")

@orders_service.get("/orders")
async def orders_list(user_id: Optional[int] = None):
    orders = [
        {"id": 1, "user_id": 1, "product_id": 1, "total": 999.99},
        {"id": 2, "user_id": 1, "product_id": 2, "total": 29.99}
    ]
    
    if user_id:
        orders = [o for o in orders if o["user_id"] == user_id]
    
    return orders

@orders_service.post("/orders")
async def orders_create(order_data: Dict):
    return {"id": 3, **order_data, "status": "pending"}


if __name__ == "__main__":
    import uvicorn
    print("""
    API Gateway Pattern Demo
    
    Start the API Gateway:
        uvicorn 13_api_gateway:app --reload --port 8000
    
    Start backend services (in separate terminals):
        uvicorn 13_api_gateway:users_service --reload --port 8001
        uvicorn 13_api_gateway:products_service --reload --port 8002
        uvicorn 13_api_gateway:orders_service --reload --port 8003
    
    Test with:
        curl -H "X-API-Key: user_key_123" http://localhost:8000/api/users
    """)
    uvicorn.run(app, host="0.0.0.0", port=8000)
