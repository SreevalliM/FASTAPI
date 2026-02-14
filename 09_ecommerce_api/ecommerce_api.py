"""
E-commerce API with Products, Orders, Background Tasks, and Custom Error Handling

Features:
- Product CRUD operations
- Order management with inventory tracking
- Background email confirmations
- Custom exception handling
- Input validation
"""
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
import logging
from datetime import datetime

from models import (
    Base, ProductDB, OrderDB,
    ProductCreate, ProductUpdate, ProductResponse,
    OrderCreate, OrderResponse, OrderStatusUpdate, OrderItemResponse,
    OrderStatus
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = "sqlite:///./ecommerce.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-commerce API",
    description="A complete e-commerce API with products, orders, and background tasks",
    version="1.0.0"
)


# ==================== Custom Exceptions ====================
class CustomAPIException(Exception):
    """Base exception for custom API errors"""
    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code


class ProductNotFoundException(CustomAPIException):
    """Raised when a product is not found"""
    def __init__(self, product_id: int):
        super().__init__(
            detail=f"Product with ID {product_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class InsufficientStockException(CustomAPIException):
    """Raised when there's not enough stock for an order"""
    def __init__(self, product_name: str, available: int, requested: int):
        super().__init__(
            detail=f"Insufficient stock for {product_name}. Available: {available}, Requested: {requested}",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class OrderNotFoundException(CustomAPIException):
    """Raised when an order is not found"""
    def __init__(self, order_id: int):
        super().__init__(
            detail=f"Order with ID {order_id} not found",
            status_code=status.HTTP_404_NOT_FOUND
        )


class InvalidOrderStateException(CustomAPIException):
    """Raised when trying to perform an invalid state transition"""
    def __init__(self, current_status: str, new_status: str):
        super().__init__(
            detail=f"Cannot change order status from {current_status} to {new_status}",
            status_code=status.HTTP_400_BAD_REQUEST
        )


# ==================== Exception Handlers ====================
@app.exception_handler(CustomAPIException)
async def custom_exception_handler(request: Request, exc: CustomAPIException):
    """Handle all custom API exceptions"""
    logger.error(f"Custom API Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "detail": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ==================== Dependencies ====================
def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== Background Tasks ====================
async def send_order_confirmation_email(order_id: int, customer_email: str, customer_name: str, total_amount: float):
    """
    Simulate sending an order confirmation email
    In production, this would integrate with an email service (SendGrid, AWS SES, etc.)
    """
    logger.info(f"📧 Sending order confirmation email to {customer_email}")
    # Simulate email processing time
    import asyncio
    await asyncio.sleep(2)
    
    logger.info(f"""
    ===== ORDER CONFIRMATION EMAIL =====
    To: {customer_email}
    Subject: Order #{order_id} Confirmed
    
    Dear {customer_name},
    
    Your order #{order_id} has been confirmed!
    Total Amount: ${total_amount:.2f}
    
    Thank you for your purchase!
    ====================================
    """)


async def send_status_update_email(order_id: int, customer_email: str, new_status: str):
    """Send email notification when order status changes"""
    logger.info(f"📧 Sending status update email to {customer_email}")
    import asyncio
    await asyncio.sleep(1)
    
    logger.info(f"""
    ===== ORDER STATUS UPDATE =====
    To: {customer_email}
    Subject: Order #{order_id} Status Update
    
    Your order #{order_id} status has been updated to: {new_status.upper()}
    ===============================
    """)


# ==================== Product Endpoints ====================
@app.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, tags=["Products"])
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product"""
    db_product = ProductDB(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    logger.info(f"✅ Created product: {db_product.name} (ID: {db_product.id})")
    return db_product


@app.get("/products", response_model=List[ProductResponse], tags=["Products"])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all products with optional filters"""
    query = db.query(ProductDB)
    
    if category:
        query = query.filter(ProductDB.category == category)
    if min_price is not None:
        query = query.filter(ProductDB.price >= min_price)
    if max_price is not None:
        query = query.filter(ProductDB.price <= max_price)
    if in_stock:
        query = query.filter(ProductDB.stock > 0)
    
    products = query.offset(skip).limit(limit).all()
    return products


@app.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not product:
        raise ProductNotFoundException(product_id)
    return product


@app.put("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
async def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    """Update a product"""
    db_product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not db_product:
        raise ProductNotFoundException(product_id)
    
    # Update only provided fields
    update_data = product_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    logger.info(f"✅ Updated product: {db_product.name} (ID: {db_product.id})")
    return db_product


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Products"])
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product"""
    db_product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
    if not db_product:
        raise ProductNotFoundException(product_id)
    
    db.delete(db_product)
    db.commit()
    logger.info(f"🗑️  Deleted product: {db_product.name} (ID: {product_id})")
    return None


# ==================== Order Endpoints ====================
@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, tags=["Orders"])
async def create_order(
    order: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new order with inventory management and background email confirmation
    """
    total_amount = 0.0
    order_items_data = []
    
    # Validate products and calculate total
    for item in order.items:
        product = db.query(ProductDB).filter(ProductDB.id == item.product_id).first()
        if not product:
            raise ProductNotFoundException(item.product_id)
        
        # Check stock availability
        if product.stock < item.quantity:
            raise InsufficientStockException(product.name, product.stock, item.quantity)
        
        # Calculate subtotal
        subtotal = product.price * item.quantity
        total_amount += subtotal
        
        order_items_data.append({
            "product": product,
            "quantity": item.quantity,
            "price": product.price,
            "subtotal": subtotal
        })
    
    # Create order
    db_order = OrderDB(
        customer_name=order.customer_name,
        customer_email=order.customer_email,
        total_amount=total_amount,
        status=OrderStatus.pending
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Update inventory
    for item_data in order_items_data:
        product = item_data["product"]
        product.stock -= item_data["quantity"]
    
    db.commit()
    
    # Add background task for email confirmation
    background_tasks.add_task(
        send_order_confirmation_email,
        db_order.id,
        order.customer_email,
        order.customer_name,
        total_amount
    )
    
    logger.info(f"✅ Created order #{db_order.id} for {order.customer_name} - Total: ${total_amount:.2f}")
    
    # Build response with order items
    response = OrderResponse(
        id=db_order.id,
        customer_name=db_order.customer_name,
        customer_email=db_order.customer_email,
        total_amount=db_order.total_amount,
        status=db_order.status,
        created_at=db_order.created_at,
        items=[
            OrderItemResponse(
                product_id=item_data["product"].id,
                product_name=item_data["product"].name,
                quantity=item_data["quantity"],
                price_at_purchase=item_data["price"],
                subtotal=item_data["subtotal"]
            )
            for item_data in order_items_data
        ]
    )
    
    return response


@app.get("/orders", response_model=List[OrderResponse], tags=["Orders"])
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[OrderStatus] = None,
    db: Session = Depends(get_db)
):
    """List all orders with optional status filter"""
    query = db.query(OrderDB)
    
    if status_filter:
        query = query.filter(OrderDB.status == status_filter.value)
    
    orders = query.offset(skip).limit(limit).all()
    return orders


@app.get("/orders/{order_id}", response_model=OrderResponse, tags=["Orders"])
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a specific order by ID"""
    order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
    if not order:
        raise OrderNotFoundException(order_id)
    return order


@app.patch("/orders/{order_id}/status", response_model=OrderResponse, tags=["Orders"])
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Update order status and send notification email"""
    order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
    if not order:
        raise OrderNotFoundException(order_id)
    
    # Validate status transition (simple validation)
    if order.status == OrderStatus.cancelled:
        raise InvalidOrderStateException(order.status, status_update.status.value)
    if order.status == OrderStatus.delivered and status_update.status != OrderStatus.delivered:
        raise InvalidOrderStateException(order.status, status_update.status.value)
    
    old_status = order.status
    order.status = status_update.status.value
    db.commit()
    db.refresh(order)
    
    # Send status update email in background
    background_tasks.add_task(
        send_status_update_email,
        order.id,
        order.customer_email,
        status_update.status.value
    )
    
    logger.info(f"✅ Updated order #{order_id} status: {old_status} → {status_update.status.value}")
    return order


@app.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Orders"])
async def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """Cancel an order (soft delete by changing status)"""
    order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
    if not order:
        raise OrderNotFoundException(order_id)
    
    if order.status in [OrderStatus.shipped, OrderStatus.delivered]:
        raise InvalidOrderStateException(order.status, "cancelled")
    
    order.status = OrderStatus.cancelled
    db.commit()
    logger.info(f"❌ Cancelled order #{order_id}")
    return None


# ==================== Root Endpoint ====================
@app.get("/", tags=["Root"])
async def root():
    """API information"""
    return {
        "message": "Welcome to E-commerce API",
        "version": "1.0.0",
        "endpoints": {
            "products": "/products",
            "orders": "/orders",
            "docs": "/docs"
        }
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
