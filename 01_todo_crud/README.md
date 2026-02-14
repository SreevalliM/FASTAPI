# Module 1: Todo CRUD API

## 📝 Basic CRUD Operations

This module introduces the fundamentals of building a REST API with FastAPI.

## 📂 Files

- `01_todo_crud_api.py` - Complete Todo API with CRUD operations

## 🎯 Learning Objectives

- Create a basic FastAPI application
- Implement CRUD operations (Create, Read, Update, Delete)
- Use Pydantic models for request/response validation
- Work with in-memory data storage
- Handle HTTP status codes
- Use path and query parameters

## 🚀 Running the API

```bash
# From this directory
python 01_todo_crud_api.py

# Or from project root
python 01_todo_crud/01_todo_crud_api.py
```

Visit: http://localhost:8000/docs

## 📚 Concepts Covered

- FastAPI application setup
- Pydantic models
- Path parameters (`/todos/{id}`)
- Query parameters (`?completed=true`)
- HTTP methods (GET, POST, PUT, DELETE)
- Status codes (200, 201, 404)
- Response models

## 🧪 Test Endpoints

```bash
# Create a todo
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "description": "Complete tutorial"}'

# Get all todos
curl http://localhost:8000/todos

# Get specific todo
curl http://localhost:8000/todos/1

# Update todo
curl -X PUT http://localhost:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Learn FastAPI", "completed": true}'

# Delete todo
curl -X DELETE http://localhost:8000/todos/1
```

## ➡️ Next Module

[Module 2: Request Validation](../02_request_validation/)
