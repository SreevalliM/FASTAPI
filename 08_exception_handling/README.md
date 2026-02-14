# 08 - Exception Handling 🚨

Complete guide to exception handling in FastAPI applications, covering custom exceptions, global error handlers, and validation errors.

## 📚 Overview

This module teaches you how to:
- Use FastAPI's built-in `HTTPException`
- Create custom exception classes for domain-specific errors
- Register global exception handlers
- Customize validation error responses
- Implement exception hierarchies
- Follow best practices for error handling

## 📁 Files

- **[08_exception_handling_basic.py](08_exception_handling_basic.py)** - Basic HTTPException usage and patterns
- **[08_custom_exceptions.py](08_custom_exceptions.py)** - Custom exceptions and global handlers
- **[08_EXCEPTION_HANDLING_TUTORIAL.md](08_EXCEPTION_HANDLING_TUTORIAL.md)** - Comprehensive tutorial
- **[EXCEPTION_HANDLING_CHEATSHEET.md](EXCEPTION_HANDLING_CHEATSHEET.md)** - Quick reference guide
- **[test_exception_handling.py](test_exception_handling.py)** - Test suite
- **[manual_test.py](manual_test.py)** - Manual test script
- **[quickstart.sh](quickstart.sh)** - Quick setup and run script

## 🚀 Quick Start

### Option 1: Using the Quickstart Script
```bash
cd 08_exception_handling
chmod +x quickstart.sh
./quickstart.sh
```

### Option 2: Manual Setup

1. **Activate virtual environment**:
   ```bash
   cd ..
   source fastapi-env/bin/activate
   ```

2. **Run the basic example**:
   ```bash
   python 08_exception_handling/08_exception_handling_basic.py
   ```

3. **Or run the custom exceptions example**:
   ```bash
   python 08_exception_handling/08_custom_exceptions.py
   ```

4. **Visit the interactive docs**:
   - Open http://127.0.0.1:8000/docs
   - Test the endpoints

## 📖 What You'll Learn

### 1. HTTPException Basics
```python
from fastapi import HTTPException, status

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    return items_db[item_id]
```

### 2. Custom Exception Classes
```python
class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id
        self.message = f"Item {item_id} not found"
        super().__init__(self.message)

class InsufficientStockError(Exception):
    def __init__(self, item_id: int, requested: int, available: int):
        self.item_id = item_id
        self.requested = requested
        self.available = available
```

### 3. Global Exception Handlers
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": "ItemNotFound",
            "message": exc.message,
            "item_id": exc.item_id
        }
    )
```

### 4. Custom Validation Error Handling
```python
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": exc.errors()
        }
    )
```

## 🎯 Key Concepts

### HTTP Status Codes
- **200 OK** - Success
- **201 Created** - Resource created
- **204 No Content** - Success, no content
- **400 Bad Request** - Invalid request
- **401 Unauthorized** - Not authenticated
- **403 Forbidden** - Not authorized
- **404 Not Found** - Resource not found
- **409 Conflict** - Duplicate resource
- **422 Unprocessable Entity** - Validation error
- **429 Too Many Requests** - Rate limit exceeded
- **500 Internal Server Error** - Server error

### Exception Handler Order
Exception handlers should be ordered from most specific to most general:
```python
# 1. Specific custom exceptions
@app.exception_handler(ItemNotFoundError)

# 2. Base class for custom exceptions
@app.exception_handler(BusinessLogicError)

# 3. Python built-ins
@app.exception_handler(ValueError)

# 4. Catch-all (last resort)
@app.exception_handler(Exception)
```

### Error Response Format
Consistent error responses make your API easier to use:
```python
{
    "error": "ErrorType",
    "message": "Human readable description",
    "timestamp": "2026-02-14T10:30:00Z",
    "path": "/api/endpoint"
}
```

## 🧪 Testing

Run the test suite:
```bash
pytest test_exception_handling.py -v
```

Run manual tests:
```bash
python manual_test.py
```

## 📝 Examples

### Example 1: Resource Not Found
```bash
curl http://127.0.0.1:8000/items/999
```

Response:
```json
{
    "error": "ItemNotFound",
    "message": "Item with id 999 not found",
    "item_id": 999,
    "timestamp": "2026-02-14T10:30:00Z"
}
```

### Example 2: Validation Error
```bash
curl -X POST http://127.0.0.1:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "", "price": -10, "quantity": -5}'
```

Response:
```json
{
    "error": "ValidationError",
    "message": "Request validation failed",
    "details": [
        {
            "loc": ["body", "name"],
            "msg": "ensure this value has at least 1 characters",
            "type": "value_error.any_str.min_length"
        },
        {
            "loc": ["body", "price"],
            "msg": "ensure this value is greater than 0",
            "type": "value_error.number.not_gt"
        }
    ]
}
```

### Example 3: Insufficient Stock
```bash
curl -X POST http://127.0.0.1:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"item_id": 1, "quantity": 9999}'
```

Response:
```json
{
    "error": "InsufficientStock",
    "message": "Insufficient stock for item 1. Requested: 9999, Available: 10",
    "item_id": 1,
    "requested": 9999,
    "available": 10
}
```

## 🎓 Learning Path

1. **Start with**: [08_exception_handling_basic.py](08_exception_handling_basic.py)
   - Understand HTTPException
   - Learn basic error handling
   - Practice with built-in exceptions

2. **Then study**: [08_custom_exceptions.py](08_custom_exceptions.py)
   - Create custom exception classes
   - Implement global handlers
   - Handle validation errors

3. **Read the tutorial**: [08_EXCEPTION_HANDLING_TUTORIAL.md](08_EXCEPTION_HANDLING_TUTORIAL.md)
   - Deep dive into concepts
   - Learn best practices
   - Study common patterns

4. **Reference**: [EXCEPTION_HANDLING_CHEATSHEET.md](EXCEPTION_HANDLING_CHEATSHEET.md)
   - Quick syntax reference
   - Common patterns
   - Status code guide

## 💡 Best Practices

1. **Use Specific Exceptions**
   - Create custom exceptions for different error types
   - Include relevant context in exceptions
   - Don't use generic `Exception` for known cases

2. **Provide Clear Error Messages**
   - Make errors actionable
   - Include what went wrong and why
   - Suggest how to fix the issue

3. **Use Correct Status Codes**
   - 404 for not found
   - 400 for bad request
   - 422 for validation errors
   - 409 for conflicts

4. **Log Appropriately**
   - Log detailed information server-side
   - Return sanitized errors to clients
   - Don't expose sensitive information

5. **Test Error Handlers**
   - Write tests for all exception handlers
   - Test edge cases
   - Verify status codes and response format

6. **Maintain Consistency**
   - Use consistent error response format
   - Follow naming conventions
   - Document expected errors in API docs

## 🔗 Common Patterns

### Not Found Pattern
```python
if item_id not in items:
    raise ItemNotFoundError(item_id)
```

### Conflict Pattern
```python
if item_name_exists:
    raise ItemAlreadyExistsError(item_name)
```

### Authorization Pattern
```python
if not authenticated:
    raise UnauthorizedError()
if not has_permission:
    raise ForbiddenError()
```

### Validation Pattern
```python
if quantity <= 0:
    raise ValidationError("quantity", "must be positive")
```

## 📚 Additional Resources

- [FastAPI Error Handling Docs](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [HTTP Status Codes Reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
- [Pydantic Validation](https://docs.pydantic.dev/latest/concepts/validators/)

## 🔄 Related Modules

- [**03 - Dependency Injection**](../03_dependency_injection/README.md) - Use dependencies for error handling
- [**05 - Authentication**](../05_authentication/README.md) - Handle auth errors
- [**07 - Middleware**](../07_middleware/README.md) - Process errors in middleware

## 🎯 Next Steps

After mastering exception handling:
1. Combine with authentication for secure error handling
2. Use middleware for global error processing
3. Implement structured logging for errors
4. Create an error monitoring system
5. Build comprehensive test suites

## 📞 Troubleshooting

**Issue**: Exception handler not being called
- Check handler is registered before app starts
- Verify exception type matches exactly
- Ensure more specific handlers come before general ones

**Issue**: Validation errors not customized
- Make sure RequestValidationError handler is registered
- Check handler signature is correct
- Verify you're returning JSONResponse

**Issue**: 500 errors without details
- Check logs for actual error
- Ensure catch-all handler exists
- Verify you're not catching exceptions too early

---

**Ready to handle errors like a pro?** Start with the basic example and work your way through the tutorial! 🚀
