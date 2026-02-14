# 🛒 E-commerce API - Practice Project

A comprehensive FastAPI project demonstrating:
- ✅ **Product Management** (CRUD operations)
- 📦 **Order Management** (with inventory tracking)
- 📧 **Background Tasks** (email confirmations)
- ⚡ **Custom Error Handling** (custom exceptions and handlers)
- 🔍 **Input Validation** (Pydantic models)
- 💾 **Database Integration** (SQLite with SQLAlchemy)

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
# From project root
source ../fastapi-env/bin/activate
```

### 2. Install Dependencies (if needed)
```bash
pip install fastapi uvicorn sqlalchemy pydantic[email]
```

### 3. Run the API
```bash
cd 09_ecommerce_api
python ecommerce_api.py
```

Or use uvicorn directly:
```bash
uvicorn ecommerce_api:app --reload
```

### 4. Access the API
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **API Base URL**: http://localhost:8000

## 📚 API Endpoints

### Products Endpoints

#### Create Product
```bash
POST /products
```
```json
{
  "name": "Laptop",
  "description": "High-performance laptop",
  "price": 999.99,
  "stock": 50,
  "category": "Electronics"
}
```

#### List Products
```bash
GET /products?category=Electronics&in_stock=true&min_price=100&max_price=2000
```

#### Get Product
```bash
GET /products/{product_id}
```

#### Update Product
```bash
PUT /products/{product_id}
```
```json
{
  "price": 899.99,
  "stock": 45
}
```

#### Delete Product
```bash
DELETE /products/{product_id}
```

### Orders Endpoints

#### Create Order
```bash
POST /orders
```
```json
{
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 2,
      "quantity": 1
    }
  ]
}
```

**Features:**
- ✅ Validates product existence
- ✅ Checks stock availability
- ✅ Updates inventory automatically
- ✅ Sends confirmation email in background

#### List Orders
```bash
GET /orders?status_filter=pending
```

#### Get Order
```bash
GET /orders/{order_id}
```

#### Update Order Status
```bash
PATCH /orders/{order_id}/status
```
```json
{
  "status": "confirmed"
}
```

**Status Options:**
- `pending`
- `confirmed`
- `shipped`
- `delivered`
- `cancelled`

**Features:**
- ✅ Validates status transitions
- ✅ Sends status update email in background

#### Cancel Order
```bash
DELETE /orders/{order_id}
```

## 🧪 Testing with curl

### 1. Create Some Products
```bash
# Create Laptop
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gaming Laptop",
    "description": "High-end gaming laptop with RTX 4080",
    "price": 1999.99,
    "stock": 10,
    "category": "Electronics"
  }'

# Create Mouse
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wireless Mouse",
    "description": "Ergonomic wireless mouse",
    "price": 49.99,
    "stock": 100,
    "category": "Electronics"
  }'

# Create Keyboard
curl -X POST "http://localhost:8000/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mechanical Keyboard",
    "description": "RGB mechanical keyboard",
    "price": 129.99,
    "stock": 50,
    "category": "Electronics"
  }'
```

### 2. List All Products
```bash
curl "http://localhost:8000/products"
```

### 3. Create an Order
```bash
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Alice Johnson",
    "customer_email": "alice@example.com",
    "items": [
      {"product_id": 1, "quantity": 1},
      {"product_id": 2, "quantity": 2}
    ]
  }'
```

### 4. Update Order Status
```bash
# Replace {order_id} with actual order ID
curl -X PATCH "http://localhost:8000/orders/1/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "confirmed"}'
```

### 5. Test Error Handling

#### Product Not Found
```bash
curl "http://localhost:8000/products/999"
```

#### Insufficient Stock
```bash
# First, check product stock
curl "http://localhost:8000/products/1"

# Try to order more than available
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Bob Smith",
    "customer_email": "bob@example.com",
    "items": [
      {"product_id": 1, "quantity": 1000}
    ]
  }'
```

#### Invalid Status Transition
```bash
# Try to update a delivered order
curl -X PATCH "http://localhost:8000/orders/1/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "delivered"}'

# Then try to change it back
curl -X PATCH "http://localhost:8000/orders/1/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "pending"}'
```

## 🏗️ Project Structure

```
09_ecommerce_api/
├── ecommerce_api.py      # Main API application
├── models.py             # Database and Pydantic models
├── test_ecommerce.py     # Test file
├── README.md             # This file
└── ecommerce.db          # SQLite database (created on first run)
```

## 🎯 Key Features Demonstrated

### 1. Custom Exception Handling
Custom exception classes with automatic error formatting:
- `ProductNotFoundException`
- `InsufficientStockException`
- `OrderNotFoundException`
- `InvalidOrderStateException`

Each exception provides:
- Descriptive error messages
- Appropriate HTTP status codes
- Timestamp logging
- Consistent JSON response format

### 2. Background Tasks
Email notifications run asynchronously without blocking responses:
- Order confirmation emails
- Status update notifications
- Logging to console (simulates real email service)

### 3. Database Integration
- SQLAlchemy ORM
- Automatic table creation
- Session management via dependency injection
- Transactional inventory updates

### 4. Input Validation
Pydantic models ensure:
- Required fields are present
- Price > 0
- Stock >= 0
- Email format validation
- String length constraints

### 5. Business Logic
- Inventory tracking (stock decreases on order)
- Order status validation
- Multi-item order support
- Price calculation at purchase time

## 📊 Database Schema

### Products Table
- `id` (Integer, Primary Key)
- `name` (String, Required)
- `description` (String, Optional)
- `price` (Float, Required, > 0)
- `stock` (Integer, Required, >= 0)
- `category` (String, Optional)
- `created_at` (DateTime)

### Orders Table
- `id` (Integer, Primary Key)
- `customer_name` (String, Required)
- `customer_email` (String, Required)
- `total_amount` (Float, Required)
- `status` (String, Required)
- `created_at` (DateTime)

## 🎓 Learning Concepts

This project combines concepts from multiple modules:

1. **Module 01**: CRUD operations (Create, Read, Update, Delete)
2. **Module 02**: Request validation with Pydantic
3. **Module 03**: Dependency injection (database sessions)
4. **Module 04**: Database integration with SQLAlchemy
5. **Module 06**: Background tasks (email sending)
6. **Module 08**: Custom exception handling

## 🔧 Troubleshooting

### Database Issues
If you encounter database issues, delete the database file and restart:
```bash
rm ecommerce.db
python ecommerce_api.py
```

### Port Already in Use
Change the port in the main block:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use different port
```

### Dependencies Missing
Install all required packages:
```bash
pip install fastapi uvicorn sqlalchemy pydantic[email]
```

## 🚀 Next Steps

Enhance this project by adding:
- [ ] User authentication (JWT tokens)
- [ ] Payment processing integration
- [ ] Product reviews and ratings
- [ ] Shopping cart functionality
- [ ] Order history tracking
- [ ] Product categories with hierarchies
- [ ] Search functionality
- [ ] Real email service integration (SendGrid, AWS SES)
- [ ] PostgreSQL instead of SQLite
- [ ] API rate limiting
- [ ] Caching with Redis
- [ ] Unit and integration tests

## 📝 Notes

- The database file (`ecommerce.db`) is created automatically on first run
- Background email tasks are simulated with console logging
- Stock is automatically updated when orders are created
- Order status transitions are validated to prevent invalid states
- All timestamps are in UTC

## 🎉 Success!

You now have a working e-commerce API! Visit http://localhost:8000/docs to explore the interactive documentation.
