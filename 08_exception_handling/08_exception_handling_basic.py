"""
FastAPI Exception Handling - Basic Examples
==========================================

This module demonstrates basic exception handling patterns in FastAPI:
1. HTTPException - Built-in FastAPI exceptions
2. Request validation errors
3. Custom status codes and headers
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional

app = FastAPI(title="Exception Handling Basic", version="1.0.0")


# ============================================================================
# Data Models
# ============================================================================

class Item(BaseModel):
    """Item model with validation"""
    name: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0, description="Price must be positive")
    quantity: int = Field(..., ge=0, description="Quantity cannot be negative")
    description: Optional[str] = None

    @validator('name')
    def name_must_not_contain_special_chars(cls, v):
        if any(char in v for char in ['<', '>', '&', '"', "'"]):
            raise ValueError('name contains invalid special characters')
        return v


# In-memory storage
items_db = {
    1: {"id": 1, "name": "Laptop", "price": 999.99, "quantity": 10},
    2: {"id": 2, "name": "Mouse", "price": 25.50, "quantity": 50},
    3: {"id": 3, "name": "Keyboard", "price": 75.00, "quantity": 30}
}


# ============================================================================
# Basic HTTPException Examples
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Exception Handling API",
        "endpoints": [
            "/items/{item_id} - Get item by ID",
            "/items - Create new item",
            "/items/{item_id} - Update item",
            "/items/{item_id} - Delete item",
            "/protected - Protected endpoint (requires header)",
            "/divide/{a}/{b} - Division operation"
        ]
    }


@app.get("/items/{item_id}")
async def get_item(item_id: int):
    """
    Get an item by ID
    
    Raises:
        HTTPException: 404 if item not found
    """
    if item_id not in items_db:
        # Basic HTTPException with status code and detail message
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    return items_db[item_id]


@app.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    """
    Create a new item
    
    Automatic validation errors are handled by FastAPI
    """
    new_id = max(items_db.keys()) + 1 if items_db else 1
    
    item_dict = item.dict()
    item_dict["id"] = new_id
    items_db[new_id] = item_dict
    
    return item_dict


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    """
    Update an existing item
    
    Raises:
        HTTPException: 404 if item not found
    """
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    item_dict = item.dict()
    item_dict["id"] = item_id
    items_db[item_id] = item_dict
    
    return item_dict


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """
    Delete an item
    
    Raises:
        HTTPException: 404 if item not found
        HTTPException: 400 if item has quantity > 0
    """
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    
    item = items_db[item_id]
    if item.get("quantity", 0) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete item with remaining quantity: {item['quantity']}"
        )
    
    del items_db[item_id]
    return None


# ============================================================================
# HTTPException with Custom Headers
# ============================================================================

@app.get("/protected")
async def protected_endpoint(request: Request):
    """
    Protected endpoint that requires a specific header
    
    Raises:
        HTTPException: 401 with WWW-Authenticate header if token missing
    """
    token = request.headers.get("X-API-Key")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    if token != "secret-key-123":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return {"message": "Access granted", "data": "Protected resource"}


# ============================================================================
# Error Handling in Business Logic
# ============================================================================

@app.get("/divide/{a}/{b}")
async def divide_numbers(a: float, b: float):
    """
    Divide two numbers
    
    Raises:
        HTTPException: 400 if division by zero
    """
    if b == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Division by zero is not allowed"
        )
    
    result = a / b
    return {"a": a, "b": b, "result": result}


# ============================================================================
# Testing Validation Errors
# ============================================================================

@app.get("/items")
async def list_items(
    skip: int = Field(default=0, ge=0, description="Number of items to skip"),
    limit: int = Field(default=10, ge=1, le=100, description="Max items to return")
):
    """
    List items with pagination
    
    Query parameters are automatically validated by FastAPI
    """
    items_list = list(items_db.values())
    return {
        "total": len(items_list),
        "skip": skip,
        "limit": limit,
        "items": items_list[skip:skip+limit]
    }


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("Starting Exception Handling Basic API...")
    print("API Documentation: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
