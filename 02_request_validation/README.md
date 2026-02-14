# Module 2: Request Validation

## ✅ Advanced Request Validation

This module covers comprehensive request validation using Pydantic.

## 📂 Files

- `02_request_validation.py` - User API with extensive validation examples

## 🎯 Learning Objectives

- Use Pydantic Field validators
- Implement custom validation logic
- Handle validation errors
- Use computed fields
- Work with complex data types (email, URLs, dates)
- Apply validation constraints (min/max length, regex patterns)

## 🚀 Running the API

```bash
# From this directory
python 02_request_validation.py

# Or from project root
python 02_request_validation/02_request_validation.py
```

Visit: http://localhost:8000/docs

## 📚 Concepts Covered

- Field validators (`Field(min_length=3)`)
- Email validation
- Regular expressions
- Password strength validation
- Age calculation with computed fields
- Custom validation methods
- Validation error handling
- Multiple validation examples

## 🧪 Test Validation

```bash
# Valid user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "StrongPass123!",
    "age": 25
  }'

# Invalid username (too short)
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "ab", "email": "test@test.com", "password": "Pass123!", "age": 25}'

# Invalid email
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "email": "invalid-email", "password": "Pass123!", "age": 25}'
```

## ➡️ Next Module

[Module 3: Dependency Injection](../03_dependency_injection/)
