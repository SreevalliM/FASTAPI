# Module 3: Dependency Injection

## 🔌 Dependency Injection Patterns

This module teaches FastAPI's powerful dependency injection system.

## 📂 Files

- `03_dependency_injection.py` - Comprehensive DI examples
- `03_DI_TUTORIAL.md` - Detailed tutorial
- `DEPENDENCY_CHEATSHEET.md` - Quick reference
- `test_dependency_injection.py` - Test examples

## 🎯 Learning Objectives

- Understand dependency injection concepts
- Create and use dependencies
- Implement authentication dependencies
- Use dependency injection for database sessions
- Share logic across endpoints
- Test with dependency overrides

## 🚀 Running the API

```bash
# From this directory
python 03_dependency_injection.py

# Or from project root
python 03_dependency_injection/03_dependency_injection.py
```

Visit: http://localhost:8000/docs

## 📚 Concepts Covered

- Simple dependencies
- Dependencies with parameters
- Class-based dependencies
- Sub-dependencies (dependencies of dependencies)
- Authentication dependencies
- Caching with dependencies
- Dependency overrides for testing

## 📖 Documentation

- **[03_DI_TUTORIAL.md](03_DI_TUTORIAL.md)** - Complete tutorial
- **[DEPENDENCY_CHEATSHEET.md](DEPENDENCY_CHEATSHEET.md)** - Quick reference

## 🧪 Test Examples

```bash
# Endpoint with authentication
curl -H "X-API-Key: secret-key" http://localhost:8000/protected

# Endpoint with pagination dependency
curl "http://localhost:8000/items?skip=0&limit=10"

# Run tests
pytest test_dependency_injection.py
```

## ➡️ Next Module

[Module 4: Database Integration](../04_database_integration/)
