# FastAPI Exception Handling Cheatsheet

Quick reference for exception handling in FastAPI.

## Table of Contents
- [HTTPException](#httpexception)
- [Custom Exceptions](#custom-exceptions)
- [Exception Handlers](#exception-handlers)
- [Validation Errors](#validation-errors)
- [Status Codes](#status-codes)
- [Common Patterns](#common-patterns)

## HTTPException

### Basic Usage
```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Item not found"
)
```

### With Headers
```python
raise HTTPException(
    status_code=401,
    detail="Not authenticated",
    headers={"WWW-Authenticate": "Bearer"}
)
```

### With Detail Object
```python
raise HTTPException(
    status_code=422,
    detail={
        "error": "ValidationFailed",
        "fields": ["email", "password"]
    }
)
```

## Custom Exceptions

### Simple Custom Exception
```python
class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id
        super().__init__(f"Item {item_id} not found")
```

### Exception with Multiple Attributes
```python
class InsufficientStockError(Exception):
    def __init__(self, item_id: int, requested: int, available: int):
        self.item_id = item_id
        self.requested = requested
        self.available = available
        self.message = f"Not enough stock: {available}/{requested}"
        super().__init__(self.message)
```

### Exception Hierarchy
```python
class BaseAPIError(Exception):
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(message)

class NotFoundError(BaseAPIError):
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", "NOT_FOUND")

class ConflictError(BaseAPIError):
    def __init__(self, message: str):
        super().__init__(message, "CONFLICT")
```

## Exception Handlers

### Basic Handler
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": "NotFound", "item_id": exc.item_id}
    )
```

### Handler with Logging
```python
import logging
logger = logging.getLogger(__name__)

@app.exception_handler(CustomError)
async def custom_error_handler(request: Request, exc: CustomError):
    logger.error(f"Error on {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={"error": exc.message}
    )
```

### Catch-All Handler
```python
@app.exception_handler(Exception)
async def general_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
```

### Handler for Python Built-ins
```python
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"error": "ValueError", "message": str(exc)}
    )

@app.exception_handler(KeyError)
async def key_error_handler(request: Request, exc: KeyError):
    return JSONResponse(
        status_code=404,
        content={"error": "KeyNotFound", "key": str(exc)}
    )
```

## Validation Errors

### Custom Validation Error Handler
```python
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "details": exc.errors(),
            "body": jsonable_encoder(exc.body)
        }
    )
```

### Pydantic Validators
```python
from pydantic import BaseModel, validator, Field

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0)
    
    @validator('name')
    def name_must_be_alphanumeric(cls, v):
        if not v.replace(' ', '').isalnum():
            raise ValueError('must be alphanumeric')
        return v
```

## Status Codes

### Import
```python
from fastapi import status
```

### 2xx Success
```python
status.HTTP_200_OK                    # 200
status.HTTP_201_CREATED               # 201
status.HTTP_202_ACCEPTED              # 202
status.HTTP_204_NO_CONTENT            # 204
```

### 3xx Redirection
```python
status.HTTP_301_MOVED_PERMANENTLY     # 301
status.HTTP_302_FOUND                 # 302
status.HTTP_304_NOT_MODIFIED          # 304
```

### 4xx Client Errors
```python
status.HTTP_400_BAD_REQUEST           # 400 - Invalid request
status.HTTP_401_UNAUTHORIZED          # 401 - Not authenticated
status.HTTP_403_FORBIDDEN             # 403 - Not authorized
status.HTTP_404_NOT_FOUND             # 404 - Resource not found
status.HTTP_405_METHOD_NOT_ALLOWED    # 405 - Method not allowed
status.HTTP_409_CONFLICT              # 409 - Duplicate/conflict
status.HTTP_422_UNPROCESSABLE_ENTITY  # 422 - Validation error
status.HTTP_429_TOO_MANY_REQUESTS     # 429 - Rate limit
```

### 5xx Server Errors
```python
status.HTTP_500_INTERNAL_SERVER_ERROR # 500 - Server error
status.HTTP_501_NOT_IMPLEMENTED       # 501 - Not implemented
status.HTTP_503_SERVICE_UNAVAILABLE   # 503 - Service down
```

## Common Patterns

### Not Found Pattern
```python
# Exception
class NotFoundError(Exception):
    def __init__(self, resource: str, id: Any):
        self.resource = resource
        self.id = id

# Handler
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": f"{exc.resource} not found", "id": str(exc.id)}
    )

# Usage
if item_id not in items:
    raise NotFoundError("Item", item_id)
```

### Conflict Pattern
```python
# Exception
class ConflictError(Exception):
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field

# Handler
@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(
        status_code=409,
        content={"error": "Conflict", "message": exc.message, "field": exc.field}
    )

# Usage
if email_exists:
    raise ConflictError("Email already registered", field="email")
```

### Authorization Pattern
```python
# Exceptions
class UnauthorizedError(Exception):
    """Not authenticated"""
    pass

class ForbiddenError(Exception):
    """Authenticated but not authorized"""
    pass

# Handlers
@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: UnauthorizedError):
    return JSONResponse(
        status_code=401,
        content={"error": "Unauthorized"},
        headers={"WWW-Authenticate": "Bearer"}
    )

@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(
        status_code=403,
        content={"error": "Forbidden"}
    )

# Usage
if not token:
    raise UnauthorizedError()
if not has_permission:
    raise ForbiddenError()
```

### Rate Limiting Pattern
```python
class RateLimitError(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after

@app.exception_handler(RateLimitError)
async def rate_limit_handler(request: Request, exc: RateLimitError):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "retry_after": exc.retry_after
        },
        headers={"Retry-After": str(exc.retry_after)}
    )
```

### Validation Pattern with Details
```python
class ValidationError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        self.errors = [{
            "field": field,
            "message": message
        }]

@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationFailed",
            "errors": exc.errors
        }
    )
```

## Response Format Examples

### Standard Error Response
```python
{
    "error": "ErrorType",
    "message": "Human readable message",
    "timestamp": "2026-02-14T10:30:00Z",
    "path": "/api/items/123"
}
```

### Error with Details
```python
{
    "error": "ValidationError",
    "message": "Request validation failed",
    "details": [
        {
            "loc": ["body", "price"],
            "msg": "ensure this value is greater than 0",
            "type": "value_error.number.not_gt"
        }
    ]
}
```

### Error with Context
```python
{
    "error": "InsufficientStock",
    "message": "Not enough items in stock",
    "item_id": 123,
    "requested": 10,
    "available": 5
}
```

## Testing

### Test Exception
```python
from fastapi.testclient import TestClient

def test_not_found():
    client = TestClient(app)
    response = client.get("/items/999")
    assert response.status_code == 404
    assert "error" in response.json()
```

### Test Validation
```python
def test_validation_error():
    client = TestClient(app)
    response = client.post("/items", json={"price": -10})
    assert response.status_code == 422
```

### Test Custom Exception
```python
def test_custom_exception():
    client = TestClient(app)
    response = client.post("/orders", json={"quantity": 9999})
    assert response.status_code == 400
    assert response.json()["error"] == "InsufficientStock"
```

## Best Practices

✅ **Do:**
- Use specific exception classes
- Include relevant context in exceptions
- Log errors appropriately
- Use correct HTTP status codes
- Return consistent error formats
- Test exception handlers

❌ **Don't:**
- Use generic Exception for known cases
- Expose sensitive information in errors
- Return stack traces to clients
- Use wrong HTTP status codes
- Ignore error logging

## Quick Reference

| Scenario | Status Code | Exception |
|----------|-------------|-----------|
| Resource not found | 404 | NotFoundError |
| Invalid input | 400 | BadRequestError |
| Validation failed | 422 | ValidationError |
| Not authenticated | 401 | UnauthorizedError |
| Not authorized | 403 | ForbiddenError |
| Duplicate resource | 409 | ConflictError |
| Rate limit exceeded | 429 | RateLimitError |
| Server error | 500 | Exception |

## See Also

- [Full Tutorial](08_EXCEPTION_HANDLING_TUTORIAL.md)
- [Basic Examples](08_exception_handling_basic.py)
- [Custom Exceptions](08_custom_exceptions.py)
- [Test Suite](test_exception_handling.py)
