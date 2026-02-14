"""
Microservices Architecture with FastAPI

Demonstrates a complete microservices setup:
- Independent services (Users, Products, Orders)
- Service-to-service communication
- Event-driven architecture with message bus
- Saga pattern for distributed transactions
- Health checks and service discovery

Architecture:
┌─────────────────┐
│  API Gateway    │
└────────┬────────┘
         │
    ┌────┴─────┬────────┬───────┐
    │          │        │       │
┌───▼───┐  ┌──▼───┐ ┌──▼───┐  ┌▼────────┐
│ Users │  │ Prod │ │Orders│  │ Message │
│Service│  │Service│ │Service│  │  Bus   │
└───────┘  └──────┘ └──────┘  └─────────┘

Run each service in a separate terminal:
    python 13_microservices_example.py users
    python 13_microservices_example.py products
    python 13_microservices_example.py orders
    python 13_microservices_example.py message_bus
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional, Callable
from datetime import datetime
from enum import Enum
import asyncio
import httpx
import json
import sys
import uuid


# ====================================
# SHARED MODELS & EVENTS
# ====================================

class EventType(str, Enum):
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    PRODUCT_CREATED = "product.created"
    PRODUCT_STOCK_UPDATED = "product.stock_updated"
    ORDER_CREATED = "order.created"
    ORDER_CONFIRMED = "order.confirmed"
    ORDER_CANCELLED = "order.cancelled"


class Event(BaseModel):
    """Base event model for event-driven communication"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict
    source_service: str


class ServiceHealth(BaseModel):
    service_name: str
    status: str
    version: str
    uptime_seconds: float
    timestamp: datetime


# ====================================
# MESSAGE BUS (Simple In-Memory)
# ====================================

class MessageBus:
    """
    Simple in-memory message bus for event-driven communication.
    In production, use RabbitMQ, Kafka, or AWS SQS.
    """
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_store: List[Event] = []
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe to an event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    async def publish(self, event: Event):
        """Publish an event to all subscribers"""
        self.event_store.append(event)
        
        if event.type in self.subscribers:
            for handler in self.subscribers[event.type]:
                try:
                    await handler(event)
                except Exception as e:
                    print(f"Error handling event {event.type}: {e}")
    
    def get_events(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[Event]:
        """Get recent events"""
        events = self.event_store
        
        if event_type:
            events = [e for e in events if e.type == event_type]
        
        return events[-limit:]


# Global message bus instance (in production, use proper message broker)
message_bus = MessageBus()


# ====================================
# USERS MICROSERVICE
# ====================================

class User(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    username: str
    full_name: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


users_db: Dict[int, User] = {}
users_next_id = 1


def create_users_service() -> FastAPI:
    """Create Users microservice"""
    service = FastAPI(title="Users Service", version="1.0.0")
    service_start_time = datetime.utcnow()
    
    @service.get("/")
    async def root():
        return {
            "service": "users",
            "version": "1.0.0",
            "endpoints": ["/users", "/users/{id}", "/health"]
        }
    
    @service.get("/health", response_model=ServiceHealth)
    async def health():
        uptime = (datetime.utcnow() - service_start_time).total_seconds()
        return ServiceHealth(
            service_name="users",
            status="healthy",
            version="1.0.0",
            uptime_seconds=uptime,
            timestamp=datetime.utcnow()
        )
    
    @service.post("/users", status_code=201)
    async def create_user(user: User):
        global users_next_id
        user.id = users_next_id
        users_next_id += 1
        users_db[user.id] = user
        
        # Publish event
        event = Event(
            type=EventType.USER_CREATED,
            data=user.dict(),
            source_service="users"
        )
        await message_bus.publish(event)
        
        return user
    
    @service.get("/users")
    async def list_users():
        return list(users_db.values())
    
    @service.get("/users/{user_id}")
    async def get_user(user_id: int):
        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        return users_db[user_id]
    
    @service.put("/users/{user_id}")
    async def update_user(user_id: int, user: User):
        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.id = user_id
        users_db[user_id] = user
        
        # Publish event
        event = Event(
            type=EventType.USER_UPDATED,
            data=user.dict(),
            source_service="users"
        )
        await message_bus.publish(event)
        
        return user
    
    return service


# ====================================
# PRODUCTS MICROSERVICE
# ====================================

class Product(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    price: float
    stock: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


products_db: Dict[int, Product] = {}
products_next_id = 1


def create_products_service() -> FastAPI:
    """Create Products microservice"""
    service = FastAPI(title="Products Service", version="1.0.0")
    service_start_time = datetime.utcnow()
    
    @service.get("/")
    async def root():
        return {
            "service": "products",
            "version": "1.0.0",
            "endpoints": ["/products", "/products/{id}", "/health"]
        }
    
    @service.get("/health", response_model=ServiceHealth)
    async def health():
        uptime = (datetime.utcnow() - service_start_time).total_seconds()
        return ServiceHealth(
            service_name="products",
            status="healthy",
            version="1.0.0",
            uptime_seconds=uptime,
            timestamp=datetime.utcnow()
        )
    
    @service.post("/products", status_code=201)
    async def create_product(product: Product):
        global products_next_id
        product.id = products_next_id
        products_next_id += 1
        products_db[product.id] = product
        
        # Publish event
        event = Event(
            type=EventType.PRODUCT_CREATED,
            data=product.dict(),
            source_service="products"
        )
        await message_bus.publish(event)
        
        return product
    
    @service.get("/products")
    async def list_products():
        return list(products_db.values())
    
    @service.get("/products/{product_id}")
    async def get_product(product_id: int):
        if product_id not in products_db:
            raise HTTPException(status_code=404, detail="Product not found")
        return products_db[product_id]
    
    @service.patch("/products/{product_id}/stock")
    async def update_stock(product_id: int, quantity: int, operation: str):
        if product_id not in products_db:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product = products_db[product_id]
        
        if operation == "add":
            product.stock += quantity
        elif operation == "subtract":
            if product.stock < quantity:
                raise HTTPException(status_code=400, detail="Insufficient stock")
            product.stock -= quantity
        else:
            raise HTTPException(status_code=400, detail="Invalid operation")
        
        # Publish event
        event = Event(
            type=EventType.PRODUCT_STOCK_UPDATED,
            data={
                "product_id": product_id,
                "old_stock": product.stock - quantity if operation == "add" else product.stock + quantity,
                "new_stock": product.stock,
                "operation": operation,
                "quantity": quantity
            },
            source_service="products"
        )
        await message_bus.publish(event)
        
        return product
    
    # Event handlers
    async def handle_order_created(event: Event):
        """Reduce stock when order is created"""
        print(f"[Products] Handling order created: {event.data.get('id')}")
        # Stock reduction is handled in the order creation flow
    
    async def handle_order_cancelled(event: Event):
        """Restore stock when order is cancelled"""
        print(f"[Products] Handling order cancelled: {event.data.get('id')}")
        order_data = event.data
        for item in order_data.get("items", []):
            product_id = item["product_id"]
            quantity = item["quantity"]
            if product_id in products_db:
                products_db[product_id].stock += quantity
    
    # Subscribe to events
    message_bus.subscribe(EventType.ORDER_CREATED, handle_order_created)
    message_bus.subscribe(EventType.ORDER_CANCELLED, handle_order_cancelled)
    
    return service


# ====================================
# ORDERS MICROSERVICE
# ====================================

class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float


class Order(BaseModel):
    id: Optional[str] = None
    user_id: int
    items: List[OrderItem]
    total: float
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)


orders_db: Dict[str, Order] = {}


def create_orders_service() -> FastAPI:
    """Create Orders microservice"""
    service = FastAPI(title="Orders Service", version="1.0.0")
    service_start_time = datetime.utcnow()
    
    # HTTP client for inter-service communication
    http_client = httpx.AsyncClient(timeout=5.0)
    
    @service.get("/")
    async def root():
        return {
            "service": "orders",
            "version": "1.0.0",
            "endpoints": ["/orders", "/orders/{id}", "/health"]
        }
    
    @service.get("/health", response_model=ServiceHealth)
    async def health():
        uptime = (datetime.utcnow() - service_start_time).total_seconds()
        return ServiceHealth(
            service_name="orders",
            status="healthy",
            version="1.0.0",
            uptime_seconds=uptime,
            timestamp=datetime.utcnow()
        )
    
    @service.post("/orders", status_code=201)
    async def create_order(order: Order):
        """
        Create order with Saga pattern for distributed transaction
        Steps:
        1. Verify user exists
        2. Verify products exist and have stock
        3. Reduce stock
        4. Create order
        5. Publish event
        """
        order.id = str(uuid.uuid4())
        
        try:
            # Step 1: Verify user exists
            user_response = await http_client.get(f"http://localhost:8001/users/{order.user_id}")
            if user_response.status_code != 200:
                raise HTTPException(status_code=400, detail="User not found")
            
            # Step 2 & 3: Verify products and reduce stock
            total = 0.0
            for item in order.items:
                # Get product
                product_response = await http_client.get(
                    f"http://localhost:8002/products/{item.product_id}"
                )
                if product_response.status_code != 200:
                    raise HTTPException(status_code=400, detail=f"Product {item.product_id} not found")
                
                product = product_response.json()
                
                # Check stock
                if product["stock"] < item.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient stock for product {item.product_id}"
                    )
                
                # Reduce stock
                stock_response = await http_client.patch(
                    f"http://localhost:8002/products/{item.product_id}/stock",
                    params={"quantity": item.quantity, "operation": "subtract"}
                )
                if stock_response.status_code != 200:
                    raise HTTPException(status_code=400, detail="Failed to update stock")
                
                item.price = product["price"]
                total += item.price * item.quantity
            
            # Step 4: Create order
            order.total = total
            orders_db[order.id] = order
            
            # Step 5: Publish event
            event = Event(
                type=EventType.ORDER_CREATED,
                data=order.dict(),
                source_service="orders"
            )
            await message_bus.publish(event)
            
            return order
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @service.get("/orders")
    async def list_orders(user_id: Optional[int] = None):
        orders = list(orders_db.values())
        if user_id:
            orders = [o for o in orders if o.user_id == user_id]
        return orders
    
    @service.get("/orders/{order_id}")
    async def get_order(order_id: str):
        if order_id not in orders_db:
            raise HTTPException(status_code=404, detail="Order not found")
        return orders_db[order_id]
    
    @service.post("/orders/{order_id}/cancel")
    async def cancel_order(order_id: str):
        """Cancel order with compensating transaction"""
        if order_id not in orders_db:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order = orders_db[order_id]
        
        if order.status != "pending":
            raise HTTPException(
                status_code=400,
                detail="Can only cancel pending orders"
            )
        
        order.status = "cancelled"
        
        # Publish event (Products service will restore stock)
        event = Event(
            type=EventType.ORDER_CANCELLED,
            data=order.dict(),
            source_service="orders"
        )
        await message_bus.publish(event)
        
        return order
    
    return service


# ====================================
# MESSAGE BUS SERVICE
# ====================================

def create_message_bus_service() -> FastAPI:
    """Create Message Bus monitoring service"""
    service = FastAPI(title="Message Bus", version="1.0.0")
    
    @service.get("/")
    async def root():
        return {
            "service": "message_bus",
            "version": "1.0.0",
            "endpoints": ["/events", "/events/{type}", "/subscribers"]
        }
    
    @service.get("/events")
    async def list_events(
        event_type: Optional[EventType] = None,
        limit: int = 100
    ):
        """List recent events"""
        events = message_bus.get_events(event_type, limit)
        return {
            "count": len(events),
            "events": [e.dict() for e in events]
        }
    
    @service.get("/events/{event_type}")
    async def get_events_by_type(event_type: EventType, limit: int = 100):
        """Get events by type"""
        events = message_bus.get_events(event_type, limit)
        return {
            "event_type": event_type,
            "count": len(events),
            "events": [e.dict() for e in events]
        }
    
    @service.get("/subscribers")
    async def list_subscribers():
        """List all event subscribers"""
        return {
            event_type: len(handlers)
            for event_type, handlers in message_bus.subscribers.items()
        }
    
    return service


# ====================================
# SERVICE RUNNER
# ====================================

def main():
    """Run a specific microservice"""
    import uvicorn
    
    if len(sys.argv) < 2:
        print("""
        Microservices Example
        
        Usage: python 13_microservices_example.py <service>
        
        Services:
            users       - Users service (port 8001)
            products    - Products service (port 8002)
            orders      - Orders service (port 8003)
            message_bus - Message bus monitoring (port 8004)
        
        Example:
            python 13_microservices_example.py users
        """)
        sys.exit(1)
    
    service_name = sys.argv[1]
    
    services = {
        "users": (create_users_service(), 8001),
        "products": (create_products_service(), 8002),
        "orders": (create_orders_service(), 8003),
        "message_bus": (create_message_bus_service(), 8004)
    }
    
    if service_name not in services:
        print(f"Unknown service: {service_name}")
        print(f"Available services: {', '.join(services.keys())}")
        sys.exit(1)
    
    app, port = services[service_name]
    
    print(f"\nStarting {service_name} service on port {port}...")
    print(f"Documentation: http://localhost:{port}/docs\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
