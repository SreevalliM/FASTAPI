# 🛒 E-commerce API - Quick Reference Cheatsheet

## 🚀 Quick Start Commands

```bash
# Start the API
cd 09_ecommerce_api
python ecommerce_api.py

# Or use the quickstart script
./quickstart.sh

# Run tests
pytest test_ecommerce.py -v

# Manual testing
python manual_test.py
```

## 📚 API Endpoints Summary

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/products` | Create product |
| GET | `/products` | List products (with filters) |
| GET | `/products/{id}` | Get product by ID |
| PUT | `/products/{id}` | Update product |
| DELETE | `/products/{id}` | Delete product |

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/orders` | Create order |
| GET | `/orders` | List orders (with filters) |
| GET | `/orders/{id}` | Get order by ID |
| PATCH | `/orders/{id}/status` | Update order status |
| DELETE | `/orders/{id}` | Cancel order |

### General

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/docs` | Interactive docs |

## 📝 Request Examples

### Create Product
```json
{
  "name": "Gaming Laptop",
  "description": "High-performance laptop",
  "price": 1999.99,
  "stock": 10,
  "category": "Electronics"
}
```

### Create Order
```json
{
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "items": [
    {"product_id": 1, "quantity": 2},
    {"product_id": 2, "quantity": 1}
  ]
}
```

### Update Order Status
```json
{
  "status": "confirmed"
}
```

**Valid statuses:** `pending`, `confirmed`, `shipped`, `delivered`, `cancelled`

## 🔧 Query Parameters

### List Products
- `skip` - Number of records to skip (pagination)
- `limit` - Maximum number of records to return
- `category` - Filter by category
- `min_price` - Minimum price filter
- `max_price` - Maximum price filter
- `in_stock` - Show only products in stock (true/false)

**Example:**
```bash
GET /products?category=Electronics&in_stock=true&min_price=100
```

### List Orders
- `skip` - Number of records to skip
- `limit` - Maximum number of records to return
- `status_filter` - Filter by order status

**Example:**
```bash
GET /orders?status_filter=pending&limit=10
```

## 🎯 Custom Exceptions

| Exception | Status Code | When Raised |
|-----------|-------------|-------------|
| `ProductNotFoundException` | 404 | Product ID not found |
| `InsufficientStockException` | 400 | Not enough stock for order |
| `OrderNotFoundException` | 404 | Order ID not found |
| `InvalidOrderStateException` | 400 | Invalid status transition |

## 📧 Background Tasks

### Order Confirmation Email
- **Triggered:** When order is created
- **Delay:** 2 seconds (simulated)
- **Content:** Order ID, customer info, total amount

### Status Update Email
- **Triggered:** When order status changes
- **Delay:** 1 second (simulated)
- **Content:** Order ID, new status

*Note: Emails are logged to console in this demo*

## 📊 Business Logic

### Inventory Management
- Stock automatically decreases when order is created
- Validates stock availability before order creation
- Prevents orders when insufficient stock

### Order Status Flow
```
pending → confirmed → shipped → delivered
                ↓
            cancelled
```

**Rules:**
- Cannot change from `delivered` to any other status
- Cannot change from `cancelled` to any other status
- Can cancel only if status is `pending` or `confirmed`

## 🧪 Testing Scenarios

### Test Insufficient Stock
1. Create product with stock = 5
2. Try to order quantity = 10
3. Should get 400 error

### Test Invalid Status Transition
1. Create order (status = pending)
2. Update to `delivered`
3. Try to update to `pending`
4. Should get 400 error

### Test Inventory Tracking
1. Create product with stock = 20
2. Create order with quantity = 5
3. Check product stock (should be 15)

## 🛠️ Common cURL Commands

### Create Product
```bash
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d '{"name":"Laptop","price":999.99,"stock":10}'
```

### Get All Products
```bash
curl "http://localhost:8000/products"
```

### Create Order
```bash
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name":"John Doe",
    "customer_email":"john@example.com",
    "items":[{"product_id":1,"quantity":2}]
  }'
```

### Update Order Status
```bash
curl -X PATCH "http://localhost:8000/orders/1/status" \
  -H "Content-Type: application/json" \
  -d '{"status":"confirmed"}'
```

## 💡 Key Features

✅ **CRUD Operations** - Full create, read, update, delete for products
✅ **Input Validation** - Pydantic models validate all inputs
✅ **Error Handling** - Custom exceptions with descriptive messages
✅ **Background Tasks** - Async email sending without blocking responses
✅ **Database Integration** - SQLAlchemy ORM with SQLite
✅ **Dependency Injection** - Database session management
✅ **Business Logic** - Inventory tracking and order validation
✅ **Query Filters** - Multiple filter options for products and orders

## 🐛 Troubleshooting

### Database Locked
```bash
rm ecommerce.db  # Delete and restart
```

### Port Already in Use
```python
# Change port in ecommerce_api.py
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Missing Dependencies
```bash
pip install fastapi uvicorn sqlalchemy pydantic[email]
```

## 📚 Related Modules

- **01_todo_crud** - Basic CRUD operations
- **02_request_validation** - Pydantic validation
- **03_dependency_injection** - DI patterns
- **04_database_integration** - SQLAlchemy
- **06_background_tasks** - Background tasks
- **08_exception_handling** - Custom exceptions

---

**💡 TIP:** Visit http://localhost:8000/docs for interactive API documentation!
