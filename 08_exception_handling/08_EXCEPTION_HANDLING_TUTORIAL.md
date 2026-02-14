# FastAPI Exception Handling Tutorial

Complete guide to handling exceptions in FastAPI applications.

## Table of Contents
1. [Introduction](#introduction)
2. [HTTPException Basics](#httpexception-basics)
3. [Custom Exception Classes](#custom-exception-classes)
4. [Global Exception Handlers](#global-exception-handlers)
5. [Request Validation Errors](#request-validation-errors)
6. [Exception Handler Inheritance](#exception-handler-inheritance)
7. [Best Practices](#best-practices)
8. [Common Patterns](#common-patterns)

## Introduction

Exception handling is crucial for building robust APIs. FastAPI provides:
- **HTTPException** - Built-in exception for HTTP errors
- **Custom Exception Handlers** - Define how to handle exceptions globally
- **Request Validation** - Automatic validation with customizable error responses
- **Status Codes** - Standard HTTP status codes from `starlette.status`

## HTTPException Basics

### Basic Usage

```python
from fastapi import FastAPI, HTTPException, status

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return items_db[item_id]
```

### With Custom Headers

```python
@app.get("/protected")
async def protected_resource(token: str = None):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return {"data": "protected"}
```

### Common HTTP Status Codes

```python
from fastapi import status

# 2xx Success
status.HTTP_200_OK                    # Standard success
status.HTTP_201_CREATED               # Resource created
status.HTTP_204_NO_CONTENT            # Success, no content to return

# 4xx Client Errors
status.HTTP_400_BAD_REQUEST           # Invalid request
status.HTTP_401_UNAUTHORIZED          # Authentication required
status.HTTP_403_FORBIDDEN             # Authenticated but not authorized
status.HTTP_404_NOT_FOUND             # Resource not found
status.HTTP_409_CONFLICT              # Conflict (e.g., duplicate)
status.HTTP_422_UNPROCESSABLE_ENTITY  # Validation error

# 5xx Server Errors
status.HTTP_500_INTERNAL_SERVER_ERROR # Unexpected server error
status.HTTP_503_SERVICE_UNAVAILABLE   # Service temporarily unavailable
```

## Custom Exception Classes

Create domain-specific exceptions for better error handling:

```python
class ItemNotFoundError(Exception):
    """Raised when an item is not found"""
    def __init__(self, item_id: int):
        self.item_id = item_id
        self.message = f"Item {item_id} not found"
        super().__init__(self.message)

class InsufficientStockError(Exception):
    """Raised when there's not enough stock"""
    def __init__(self, item_id: int, requested: int, available: int):
        self.item_id = item_id
        self.requested = requested
        self.available = available
        self.message = f"Insufficient stock: requested {requested}, available {available}"
        super().__init__(self.message)
```

### Using Custom Exceptions

```python
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id not in items_db:
        raise ItemNotFoundError(item_id)
    return items_db[item_id]

@app.post("/orders")
async def create_order(item_id: int, quantity: int):
    item = items_db.get(item_id)
    if not item:
        raise ItemNotFoundError(item_id)
    
    if quantity > item["stock"]:
        raise InsufficientStockError(item_id, quantity, item["stock"])
    
    # Process order...
    return {"status": "success"}
```

## Global Exception Handlers

Register handlers to catch exceptions across your entire application:

### Basic Exception Handler

```python
from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime

@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    """Handle ItemNotFoundError globally"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "ItemNotFound",
            "message": exc.message,
            "item_id": exc.item_id,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )
```

### Handler with Logging

```python
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(InsufficientStockError)
async def insufficient_stock_handler(request: Request, exc: InsufficientStockError):
    """Handle stock errors with logging"""
    logger.warning(
        f"Insufficient stock for item {exc.item_id}: "
        f"requested={exc.requested}, available={exc.available}"
    )
    
    return JSONResponse(
        status_code=400,
        content={
            "error": "InsufficientStock",
            "message": exc.message,
            "item_id": exc.item_id,
            "requested": exc.requested,
            "available": exc.available
        }
    )
```

### Catch-All Handler

```python
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

## Request Validation Errors

Customize how FastAPI handles validation errors:

### Default Behavior

FastAPI automatically validates request bodies, query parameters, and path parameters. Invalid data returns a 422 status with error details.

### Custom Validation Error Handler

```python
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Custom validation error response"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": exc.errors(),
            "body": jsonable_encoder(exc.body),
            "path": str(request.url.path)
        }
    )
```

### Validation Error Structure

```python
# Example validation error format:
{
    "error": "ValidationError",
    "message": "Request validation failed",
    "details": [
        {
            "loc": ["body", "price"],
            "msg": "ensure this value is greater than 0",
            "type": "value_error.number.not_gt"
        },
        {
            "loc": ["body", "name"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ],
    "path": "/items"
}
```

## Exception Handler Inheritance

Create exception hierarchies for flexible handling:

```python
class BusinessLogicError(Exception):
    """Base exception for business logic errors"""
    def __init__(self, message: str, error_code: str = "BUSINESS_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class InvalidOperationError(BusinessLogicError):
    """Invalid operation error"""
    def __init__(self, message: str):
        super().__init__(message, error_code="INVALID_OPERATION")

class DataConflictError(BusinessLogicError):
    """Data conflict error"""
    def __init__(self, message: str):
        super().__init__(message, error_code="DATA_CONFLICT")
```

### Handler for Base Class

```python
@app.exception_handler(BusinessLogicError)
async def business_logic_handler(request: Request, exc: BusinessLogicError):
    """Handles all BusinessLogicError subclasses"""
    return JSONResponse(
        status_code=422,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# All subclasses (InvalidOperationError, DataConflictError) 
# are automatically handled by this handler
```

## Best Practices

### 1. Use Specific Exceptions

❌ **Bad**: Generic exceptions
```python
if item_id not in items:
    raise Exception("Not found")
```

✅ **Good**: Specific custom exceptions
```python
if item_id not in items:
    raise ItemNotFoundError(item_id)
```

### 2. Include Relevant Context

❌ **Bad**: Minimal information
```python
raise HTTPException(status_code=400, detail="Bad request")
```

✅ **Good**: Detailed context
```python
raise HTTPException(
    status_code=400,
    detail=f"Invalid quantity: {quantity}. Must be between 1 and {max_quantity}"
)
```

### 3. Log Errors Appropriately

```python
@app.exception_handler(InternalError)
async def internal_error_handler(request: Request, exc: InternalError):
    # Log full details server-side
    logger.error(f"Internal error: {exc}", exc_info=True)
    
    # Return sanitized message to client
    return JSONResponse(
        status_code=500,
        content={"error": "Internal error occurred"}
    )
```

### 4. Use HTTP Status Codes Correctly

```python
# 404 - Resource not found
raise ItemNotFoundError(item_id)  # Maps to 404

# 409 - Conflict (duplicate resource)
raise ItemAlreadyExistsError(name)  # Maps to 409

# 400 - Bad request (invalid operation)
raise InvalidOperationError(msg)  # Maps to 400

# 422 - Validation error
raise ValidationError(details)  # Maps to 422

# 500 - Internal server error
# Let unexpected exceptions fall through to catch-all handler
```

### 5. Don't Expose Sensitive Information

❌ **Bad**: Exposing internal details
```python
return JSONResponse(
    status_code=500,
    content={
        "error": str(exc),
        "traceback": traceback.format_exc(),
        "database_connection": db_string
    }
)
```

✅ **Good**: Generic message for unexpected errors
```python
logger.error(f"Internal error: {exc}", exc_info=True)
return JSONResponse(
    status_code=500,
    content={"error": "An unexpected error occurred"}
)
```

### 6. Order Exception Handlers Carefully

```python
# Specific handlers first
@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(...): pass

@app.exception_handler(BusinessLogicError)
async def business_logic_handler(...): pass

# General handlers last
@app.exception_handler(Exception)
async def general_handler(...): pass
```

## Common Patterns

### 1. Not Found Pattern

```python
class NotFoundError(Exception):
    def __init__(self, resource_type: str, resource_id: Any):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} {resource_id} not found")

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "NotFound",
            "resource_type": exc.resource_type,
            "resource_id": str(exc.resource_id)
        }
    )

# Usage
if user_id not in users:
    raise NotFoundError("User", user_id)
if product_id not in products:
    raise NotFoundError("Product", product_id)
```

### 2. Conflict Pattern

```python
class ConflictError(Exception):
    def __init__(self, message: str, conflicting_field: str = None):
        self.message = message
        self.conflicting_field = conflicting_field
        super().__init__(message)

@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(
        status_code=409,
        content={
            "error": "Conflict",
            "message": exc.message,
            "field": exc.conflicting_field
        }
    )

# Usage
if email in existing_emails:
    raise ConflictError(
        f"Email {email} already exists",
        conflicting_field="email"
    )
```

### 3. Validation Pattern

```python
from pydantic import BaseModel, validator

class Item(BaseModel):
    name: str
    price: float
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @validator('name')
    def name_must_be_valid(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Name cannot be empty')
        return v
```

### 4. Authorization Pattern

```python
class UnauthorizedError(Exception):
    def __init__(self, message: str = "Unauthorized"):
        self.message = message
        super().__init__(message)

class ForbiddenError(Exception):
    def __init__(self, message: str = "Forbidden"):
        self.message = message
        super().__init__(message)

@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: UnauthorizedError):
    return JSONResponse(
        status_code=401,
        content={"error": "Unauthorized", "message": exc.message},
        headers={"WWW-Authenticate": "Bearer"}
    )

@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(
        status_code=403,
        content={"error": "Forbidden", "message": exc.message}
    )

# Usage
if not token:
    raise UnauthorizedError("Authentication required")
if not has_permission(user, resource):
    raise ForbiddenError("Insufficient permissions")
```

### 5. Rate Limiting Pattern

```python
class RateLimitExceededError(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds")

@app.exception_handler(RateLimitExceededError)
async def rate_limit_handler(request: Request, exc: RateLimitExceededError):
    return JSONResponse(
        status_code=429,
        content={
            "error": "RateLimitExceeded",
            "message": "Too many requests",
            "retry_after": exc.retry_after
        },
        headers={"Retry-After": str(exc.retry_after)}
    )
```

## Testing Exception Handlers

```python
from fastapi.testclient import TestClient

def test_item_not_found():
    client = TestClient(app)
    response = client.get("/items/999")
    
    assert response.status_code == 404
    assert response.json()["error"] == "ItemNotFound"
    assert response.json()["item_id"] == 999

def test_validation_error():
    client = TestClient(app)
    response = client.post("/items", json={"name": "", "price": -10})
    
    assert response.status_code == 422
    assert "ValidationError" in response.json()["error"]

def test_custom_exception():
    client = TestClient(app)
    response = client.post("/orders", json={"item_id": 1, "quantity": 9999})
    
    assert response.status_code == 400
    assert response.json()["error"] == "InsufficientStock"
```

## Summary

Key takeaways:
1. **Use HTTPException** for simple HTTP errors
2. **Create custom exceptions** for domain-specific errors
3. **Register global handlers** with `@app.exception_handler`
4. **Customize validation errors** with RequestValidationError handler
5. **Use exception inheritance** for flexible error handling
6. **Log appropriately** - detailed server-side, sanitized client-side
7. **Use correct HTTP status codes** for different error types
8. **Include relevant context** in error responses
9. **Don't expose sensitive information** in error messages
10. **Test your error handlers** to ensure they work correctly

## Next Steps

- Explore [middleware](../07_middleware/README.md) for request/response processing
- Learn about [background tasks](../06_background_tasks/README.md)
- Study [authentication](../05_authentication/README.md) error handling
- Check the [cheatsheet](EXCEPTION_HANDLING_CHEATSHEET.md) for quick reference
