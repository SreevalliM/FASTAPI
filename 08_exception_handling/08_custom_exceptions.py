"""
FastAPI Custom Exceptions and Global Error Handlers
==================================================

This module demonstrates advanced exception handling:
1. Custom exception classes
2. Global exception handlers
3. Exception handler inheritance
4. Request validation error customization
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Custom Exception Handling", version="1.0.0")


# ============================================================================
# Custom Exception Classes
# ============================================================================

class ItemNotFoundError(Exception):
    """Custom exception for item not found"""
    def __init__(self, item_id: int):
        self.item_id = item_id
        self.message = f"Item with id {item_id} not found"
        super().__init__(self.message)


class ItemAlreadyExistsError(Exception):
    """Custom exception for duplicate items"""
    def __init__(self, item_name: str):
        self.item_name = item_name
        self.message = f"Item with name '{item_name}' already exists"
        super().__init__(self.message)


class InsufficientStockError(Exception):
    """Custom exception for insufficient stock"""
    def __init__(self, item_id: int, requested: int, available: int):
        self.item_id = item_id
        self.requested = requested
        self.available = available
        self.message = f"Insufficient stock for item {item_id}. Requested: {requested}, Available: {available}"
        super().__init__(self.message)


class BusinessLogicError(Exception):
    """Base exception for business logic errors"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code or "BUSINESS_ERROR"
        super().__init__(self.message)


class InvalidOperationError(BusinessLogicError):
    """Exception for invalid operations"""
    def __init__(self, message: str):
        super().__init__(message, error_code="INVALID_OPERATION")


# ============================================================================
# Global Exception Handlers
# ============================================================================

@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    """
    Global handler for ItemNotFoundError
    
    Returns a structured JSON response with error details
    """
    logger.warning(f"Item not found: {exc.item_id} - Path: {request.url.path}")
    
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "ItemNotFound",
            "message": exc.message,
            "item_id": exc.item_id,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )


@app.exception_handler(ItemAlreadyExistsError)
async def item_already_exists_handler(request: Request, exc: ItemAlreadyExistsError):
    """Global handler for ItemAlreadyExistsError"""
    logger.warning(f"Duplicate item: {exc.item_name} - Path: {request.url.path}")
    
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "ItemAlreadyExists",
            "message": exc.message,
            "item_name": exc.item_name,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(InsufficientStockError)
async def insufficient_stock_handler(request: Request, exc: InsufficientStockError):
    """Global handler for InsufficientStockError"""
    logger.warning(f"Insufficient stock: {exc.message}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "InsufficientStock",
            "message": exc.message,
            "item_id": exc.item_id,
            "requested": exc.requested,
            "available": exc.available,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(BusinessLogicError)
async def business_logic_error_handler(request: Request, exc: BusinessLogicError):
    """
    Global handler for all BusinessLogicError and subclasses
    
    This demonstrates exception handler inheritance
    """
    logger.error(f"Business logic error: {exc.message} - Code: {exc.error_code}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for request validation errors
    
    This overrides FastAPI's default validation error response
    """
    logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": exc.errors(),
            "body": jsonable_encoder(exc.body) if hasattr(exc, 'body') else None,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Global handler for ValueError
    
    Demonstrates handling built-in Python exceptions
    """
    logger.error(f"ValueError on {request.url.path}: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "ValueError",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Catch-all handler for unexpected exceptions
    
    This should be the last resort for unhandled exceptions
    """
    logger.error(f"Unexpected error on {request.url.path}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )


# ============================================================================
# Data Models
# ============================================================================

class Item(BaseModel):
    """Item model with validation"""
    name: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    category: str = Field(..., min_length=1)

    @validator('category')
    def category_must_be_valid(cls, v):
        valid_categories = ['electronics', 'books', 'clothing', 'food']
        if v.lower() not in valid_categories:
            raise ValueError(f'category must be one of: {", ".join(valid_categories)}')
        return v.lower()


class OrderRequest(BaseModel):
    """Order request model"""
    item_id: int
    quantity: int = Field(..., gt=0)


# In-memory storage
items_db = {
    1: {"id": 1, "name": "Laptop", "price": 999.99, "quantity": 10, "category": "electronics"},
    2: {"id": 2, "name": "Python Book", "price": 45.00, "quantity": 50, "category": "books"},
    3: {"id": 3, "name": "T-Shirt", "price": 20.00, "quantity": 100, "category": "clothing"}
}


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Custom Exception Handling API",
        "endpoints": [
            "GET /items - List all items",
            "GET /items/{item_id} - Get item by ID",
            "POST /items - Create new item",
            "POST /orders - Place an order",
            "DELETE /items/{item_id} - Delete item",
            "GET /test-error - Trigger unexpected error"
        ]
    }


@app.get("/items")
async def list_items():
    """List all items"""
    return {"items": list(items_db.values())}


@app.get("/items/{item_id}")
async def get_item(item_id: int):
    """
    Get an item by ID
    
    Raises:
        ItemNotFoundError: If item doesn't exist
    """
    if item_id not in items_db:
        raise ItemNotFoundError(item_id)
    
    return items_db[item_id]


@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    """
    Create a new item
    
    Raises:
        ItemAlreadyExistsError: If item with same name exists
    """
    # Check for duplicate names
    for existing_item in items_db.values():
        if existing_item["name"].lower() == item.name.lower():
            raise ItemAlreadyExistsError(item.name)
    
    new_id = max(items_db.keys()) + 1 if items_db else 1
    item_dict = item.dict()
    item_dict["id"] = new_id
    items_db[new_id] = item_dict
    
    logger.info(f"Created item: {new_id} - {item.name}")
    return item_dict


@app.post("/orders", status_code=status.HTTP_201_CREATED)
async def place_order(order: OrderRequest):
    """
    Place an order for an item
    
    Raises:
        ItemNotFoundError: If item doesn't exist
        InsufficientStockError: If not enough stock available
    """
    if order.item_id not in items_db:
        raise ItemNotFoundError(order.item_id)
    
    item = items_db[order.item_id]
    available_quantity = item["quantity"]
    
    if order.quantity > available_quantity:
        raise InsufficientStockError(
            order.item_id,
            requested=order.quantity,
            available=available_quantity
        )
    
    # Update stock
    items_db[order.item_id]["quantity"] -= order.quantity
    
    total_price = item["price"] * order.quantity
    
    logger.info(f"Order placed: Item {order.item_id}, Quantity: {order.quantity}")
    
    return {
        "order_id": 12345,  # In real app, generate unique ID
        "item": item["name"],
        "quantity": order.quantity,
        "unit_price": item["price"],
        "total_price": total_price,
        "message": "Order placed successfully"
    }


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """
    Delete an item
    
    Raises:
        ItemNotFoundError: If item doesn't exist
        InvalidOperationError: If item has stock
    """
    if item_id not in items_db:
        raise ItemNotFoundError(item_id)
    
    item = items_db[item_id]
    if item["quantity"] > 0:
        raise InvalidOperationError(
            f"Cannot delete item with remaining stock: {item['quantity']} units"
        )
    
    del items_db[item_id]
    logger.info(f"Deleted item: {item_id}")
    return None


@app.get("/test-error")
async def trigger_unexpected_error():
    """
    Endpoint to test unexpected error handling
    
    This will trigger the general exception handler
    """
    # This will raise a ZeroDivisionError
    result = 1 / 0
    return {"result": result}


@app.get("/test-value-error")
async def trigger_value_error():
    """
    Endpoint to test ValueError handling
    """
    raise ValueError("This is a test ValueError for demonstration")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("Starting Custom Exception Handling API...")
    print("API Documentation: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
