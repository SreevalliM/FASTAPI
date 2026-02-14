"""
Clean Architecture Implementation with FastAPI

This module demonstrates a complete clean architecture implementation with:
- Domain Layer: Business entities and rules
- Application Layer: Use cases and services
- Infrastructure Layer: Data access, external services
- Presentation Layer: API routes and DTOs

Run: uvicorn 13_clean_architecture:app --reload
"""

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Protocol, Dict
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import uuid


# ====================================
# DOMAIN LAYER - Business Entities
# ====================================

class Product:
    """Domain entity representing a product"""
    
    def __init__(
        self,
        id: str,
        name: str,
        price: float,
        stock: int,
        created_at: datetime
    ):
        self.id = id
        self.name = name
        self._price = price
        self._stock = stock
        self.created_at = created_at
        self.updated_at = created_at
    
    @property
    def price(self) -> float:
        return self._price
    
    @price.setter
    def price(self, value: float):
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = value
        self.updated_at = datetime.utcnow()
    
    @property
    def stock(self) -> int:
        return self._stock
    
    def is_available(self) -> bool:
        """Business rule: product is available if in stock"""
        return self._stock > 0
    
    def reduce_stock(self, quantity: int) -> None:
        """Business rule: stock reduction with validation"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if quantity > self._stock:
            raise ValueError("Insufficient stock")
        self._stock -= quantity
        self.updated_at = datetime.utcnow()
    
    def increase_stock(self, quantity: int) -> None:
        """Business rule: stock increase with validation"""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        self._stock += quantity
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "available": self.is_available(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class Order:
    """Domain entity representing an order"""
    
    def __init__(
        self,
        id: str,
        customer_email: str,
        items: List[Dict],
        total: float,
        status: str = "pending"
    ):
        self.id = id
        self.customer_email = customer_email
        self.items = items
        self.total = total
        self.status = status
        self.created_at = datetime.utcnow()
    
    def can_cancel(self) -> bool:
        """Business rule: can only cancel pending orders"""
        return self.status == "pending"
    
    def cancel(self) -> None:
        """Business rule: cancel order"""
        if not self.can_cancel():
            raise ValueError("Cannot cancel order in current status")
        self.status = "cancelled"
    
    def confirm(self) -> None:
        """Business rule: confirm order"""
        if self.status != "pending":
            raise ValueError("Can only confirm pending orders")
        self.status = "confirmed"
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "customer_email": self.customer_email,
            "items": self.items,
            "total": self.total,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }


# ====================================
# INFRASTRUCTURE LAYER - Repositories
# ====================================

class ProductRepository(Protocol):
    """Port (interface) for product data access"""
    
    async def save(self, product: Product) -> Product:
        ...
    
    async def get_by_id(self, product_id: str) -> Optional[Product]:
        ...
    
    async def get_all(self) -> List[Product]:
        ...
    
    async def update(self, product: Product) -> Product:
        ...
    
    async def delete(self, product_id: str) -> bool:
        ...


class OrderRepository(Protocol):
    """Port (interface) for order data access"""
    
    async def save(self, order: Order) -> Order:
        ...
    
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        ...
    
    async def get_by_customer(self, email: str) -> List[Order]:
        ...


# In-Memory Implementation (Adapter)
class InMemoryProductRepository:
    """Concrete implementation of ProductRepository"""
    
    def __init__(self):
        self._storage: Dict[str, Product] = {}
    
    async def save(self, product: Product) -> Product:
        self._storage[product.id] = product
        return product
    
    async def get_by_id(self, product_id: str) -> Optional[Product]:
        return self._storage.get(product_id)
    
    async def get_all(self) -> List[Product]:
        return list(self._storage.values())
    
    async def update(self, product: Product) -> Product:
        if product.id not in self._storage:
            raise ValueError("Product not found")
        self._storage[product.id] = product
        return product
    
    async def delete(self, product_id: str) -> bool:
        if product_id in self._storage:
            del self._storage[product_id]
            return True
        return False


class InMemoryOrderRepository:
    """Concrete implementation of OrderRepository"""
    
    def __init__(self):
        self._storage: Dict[str, Order] = {}
    
    async def save(self, order: Order) -> Order:
        self._storage[order.id] = order
        return order
    
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        return self._storage.get(order_id)
    
    async def get_by_customer(self, email: str) -> List[Order]:
        return [
            order for order in self._storage.values()
            if order.customer_email == email
        ]


# ====================================
# APPLICATION LAYER - Services (Use Cases)
# ====================================

class ProductService:
    """Application service for product operations"""
    
    def __init__(self, repository: ProductRepository):
        self.repository = repository
    
    async def create_product(
        self,
        name: str,
        price: float,
        stock: int
    ) -> Product:
        """Use case: Create a new product"""
        # Business validation
        if price < 0:
            raise ValueError("Price cannot be negative")
        if stock < 0:
            raise ValueError("Stock cannot be negative")
        
        # Create domain entity
        product = Product(
            id=str(uuid.uuid4()),
            name=name,
            price=price,
            stock=stock,
            created_at=datetime.utcnow()
        )
        
        # Persist
        return await self.repository.save(product)
    
    async def get_product(self, product_id: str) -> Product:
        """Use case: Get product by ID"""
        product = await self.repository.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        return product
    
    async def list_products(self) -> List[Product]:
        """Use case: List all products"""
        return await self.repository.get_all()
    
    async def update_price(self, product_id: str, new_price: float) -> Product:
        """Use case: Update product price"""
        product = await self.get_product(product_id)
        product.price = new_price  # Uses domain validation
        return await self.repository.update(product)
    
    async def adjust_stock(
        self,
        product_id: str,
        quantity: int,
        operation: str
    ) -> Product:
        """Use case: Adjust product stock"""
        product = await self.get_product(product_id)
        
        if operation == "increase":
            product.increase_stock(quantity)
        elif operation == "decrease":
            product.reduce_stock(quantity)
        else:
            raise ValueError("Invalid operation")
        
        return await self.repository.update(product)


class OrderService:
    """Application service for order operations"""
    
    def __init__(
        self,
        order_repository: OrderRepository,
        product_service: ProductService
    ):
        self.order_repository = order_repository
        self.product_service = product_service
    
    async def create_order(
        self,
        customer_email: str,
        items: List[Dict[str, any]]
    ) -> Order:
        """Use case: Create a new order"""
        # Validate and calculate total
        total = 0.0
        order_items = []
        
        for item in items:
            product = await self.product_service.get_product(item["product_id"])
            
            if not product.is_available():
                raise ValueError(f"Product {product.name} is not available")
            
            quantity = item["quantity"]
            if quantity > product.stock:
                raise ValueError(
                    f"Insufficient stock for {product.name}"
                )
            
            # Reduce stock
            await self.product_service.adjust_stock(
                product.id,
                quantity,
                "decrease"
            )
            
            # Add to order items
            item_total = product.price * quantity
            total += item_total
            
            order_items.append({
                "product_id": product.id,
                "product_name": product.name,
                "quantity": quantity,
                "price": product.price,
                "subtotal": item_total
            })
        
        # Create order
        order = Order(
            id=str(uuid.uuid4()),
            customer_email=customer_email,
            items=order_items,
            total=total
        )
        
        return await self.order_repository.save(order)
    
    async def get_order(self, order_id: str) -> Order:
        """Use case: Get order by ID"""
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        return order
    
    async def cancel_order(self, order_id: str) -> Order:
        """Use case: Cancel an order"""
        order = await self.get_order(order_id)
        
        # Restore stock
        for item in order.items:
            await self.product_service.adjust_stock(
                item["product_id"],
                item["quantity"],
                "increase"
            )
        
        # Cancel order
        order.cancel()
        return await self.order_repository.save(order)
    
    async def get_customer_orders(self, email: str) -> List[Order]:
        """Use case: Get all orders for a customer"""
        return await self.order_repository.get_by_customer(email)


# ====================================
# PRESENTATION LAYER - DTOs & API
# ====================================

# Request/Response Models (DTOs)
class CreateProductRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)


class UpdatePriceRequest(BaseModel):
    price: float = Field(..., gt=0)


class AdjustStockRequest(BaseModel):
    quantity: int = Field(..., gt=0)
    operation: str = Field(..., regex="^(increase|decrease)$")


class OrderItemRequest(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)


class CreateOrderRequest(BaseModel):
    customer_email: EmailStr
    items: List[OrderItemRequest]
    
    @validator('items')
    def items_not_empty(cls, v):
        if not v:
            raise ValueError('Order must have at least one item')
        return v


class ProductResponse(BaseModel):
    id: str
    name: str
    price: float
    stock: int
    available: bool
    created_at: str
    updated_at: str


class OrderResponse(BaseModel):
    id: str
    customer_email: str
    items: List[dict]
    total: float
    status: str
    created_at: str


# FastAPI Application
app = FastAPI(
    title="Clean Architecture Example",
    description="Demonstrates clean architecture with FastAPI",
    version="1.0.0"
)

# Dependency Injection Setup
product_repository = InMemoryProductRepository()
order_repository = InMemoryOrderRepository()


def get_product_service() -> ProductService:
    """Dependency: Product Service"""
    return ProductService(product_repository)


def get_order_service(
    product_service: ProductService = Depends(get_product_service)
) -> OrderService:
    """Dependency: Order Service"""
    return OrderService(order_repository, product_service)


# API Routes
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Clean Architecture API",
        "architecture": {
            "domain": "Business entities and rules",
            "application": "Use cases and services",
            "infrastructure": "Data access and external services",
            "presentation": "API routes and DTOs"
        },
        "endpoints": {
            "products": "/products",
            "orders": "/orders",
            "docs": "/docs"
        }
    }


# Product Endpoints
@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    request: CreateProductRequest,
    service: ProductService = Depends(get_product_service)
):
    """Create a new product"""
    try:
        product = await service.create_product(
            name=request.name,
            price=request.price,
            stock=request.stock
        )
        return ProductResponse(**product.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/products", response_model=List[ProductResponse])
async def list_products(
    service: ProductService = Depends(get_product_service)
):
    """List all products"""
    products = await service.list_products()
    return [ProductResponse(**p.to_dict()) for p in products]


@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    service: ProductService = Depends(get_product_service)
):
    """Get a specific product"""
    try:
        product = await service.get_product(product_id)
        return ProductResponse(**product.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.patch("/products/{product_id}/price", response_model=ProductResponse)
async def update_product_price(
    product_id: str,
    request: UpdatePriceRequest,
    service: ProductService = Depends(get_product_service)
):
    """Update product price"""
    try:
        product = await service.update_price(product_id, request.price)
        return ProductResponse(**product.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.patch("/products/{product_id}/stock", response_model=ProductResponse)
async def adjust_product_stock(
    product_id: str,
    request: AdjustStockRequest,
    service: ProductService = Depends(get_product_service)
):
    """Adjust product stock"""
    try:
        product = await service.adjust_stock(
            product_id,
            request.quantity,
            request.operation
        )
        return ProductResponse(**product.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Order Endpoints
@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: CreateOrderRequest,
    service: OrderService = Depends(get_order_service)
):
    """Create a new order"""
    try:
        items = [item.dict() for item in request.items]
        order = await service.create_order(
            customer_email=request.customer_email,
            items=items
        )
        return OrderResponse(**order.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    service: OrderService = Depends(get_order_service)
):
    """Get a specific order"""
    try:
        order = await service.get_order(order_id)
        return OrderResponse(**order.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/orders/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    service: OrderService = Depends(get_order_service)
):
    """Cancel an order"""
    try:
        order = await service.cancel_order(order_id)
        return OrderResponse(**order.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/customers/{email}/orders", response_model=List[OrderResponse])
async def get_customer_orders(
    email: EmailStr,
    service: OrderService = Depends(get_order_service)
):
    """Get all orders for a customer"""
    orders = await service.get_customer_orders(email)
    return [OrderResponse(**o.to_dict()) for o in orders]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
