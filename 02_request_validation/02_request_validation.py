"""
FastAPI Request Validation Examples
Demonstrates: Query(), Path(), Body(), Annotated, regex validation, min/max length, numeric constraints
"""

from fastapi import FastAPI, Query, Path, Body, HTTPException
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List, Annotated
import re

app = FastAPI(
    title="Request Validation API",
    description="Comprehensive examples of FastAPI request validation",
    version="1.0.0"
)

# ==================== Pydantic Models ====================

class User(BaseModel):
    """User model with various validation constraints"""
    username: str = Field(
        ..., 
        min_length=3, 
        max_length=20,
        pattern="^[a-zA-Z0-9_]+$",  # Regex: alphanumeric and underscore only
        description="Username (3-20 chars, alphanumeric and underscore)"
    )
    email: EmailStr = Field(..., description="Valid email address")
    age: int = Field(..., ge=18, le=120, description="Age (18-120)")
    phone: Optional[str] = Field(
        None,
        pattern="^\\+?[1-9]\\d{1,14}$",  # E.164 phone format
        description="Phone number in E.164 format"
    )
    bio: Optional[str] = Field(None, max_length=500, description="User bio (max 500 chars)")

class Product(BaseModel):
    """Product model with numeric constraints"""
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0, le=1000000, description="Price must be > 0 and <= 1,000,000")
    quantity: int = Field(..., ge=0, description="Quantity must be >= 0")
    discount: Optional[float] = Field(None, ge=0, le=100, description="Discount percentage (0-100)")
    sku: str = Field(
        ...,
        pattern="^[A-Z]{3}-\\d{4}$",  # Format: ABC-1234
        description="SKU format: 3 uppercase letters, dash, 4 digits"
    )

class Review(BaseModel):
    """Review model with custom validation"""
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    comment: str = Field(..., min_length=10, max_length=1000)
    reviewer_name: str = Field(..., min_length=2, max_length=50)
    
    @field_validator('comment')
    @classmethod
    def comment_must_not_be_spam(cls, v: str) -> str:
        """Custom validator to check for spam patterns"""
        spam_words = ['spam', 'viagra', 'casino', 'winner']
        if any(word in v.lower() for word in spam_words):
            raise ValueError('Comment contains spam words')
        return v

# ==================== Query Parameter Validation ====================

@app.get("/search", tags=["Query Parameters"])
def search_items(
    # Using Query() with various constraints
    q: Annotated[str, Query(
        min_length=1,
        max_length=50,
        pattern="^[a-zA-Z0-9 ]+$",
        description="Search query (1-50 chars, alphanumeric and spaces)"
    )],
    page: Annotated[int, Query(
        ge=1,
        le=1000,
        description="Page number (1-1000)"
    )] = 1,
    limit: Annotated[int, Query(
        ge=1,
        le=100,
        description="Items per page (1-100)"
    )] = 10,
    sort_by: Annotated[Optional[str], Query(
        pattern="^(name|price|date)$",  # Only these values allowed
        description="Sort field: name, price, or date"
    )] = None,
    min_price: Annotated[Optional[float], Query(
        ge=0,
        description="Minimum price filter"
    )] = None,
    max_price: Annotated[Optional[float], Query(
        le=1000000,
        description="Maximum price filter"
    )] = None
):
    """
    Search endpoint with comprehensive query parameter validation
    
    Examples:
    - /search?q=laptop&page=1&limit=20
    - /search?q=phone&min_price=100&max_price=1000&sort_by=price
    """
    return {
        "query": q,
        "page": page,
        "limit": limit,
        "sort_by": sort_by,
        "price_range": {"min": min_price, "max": max_price},
        "results": f"Showing {limit} results for '{q}' on page {page}"
    }

# Alternative: Using Query() without Annotated (older style)
@app.get("/filter", tags=["Query Parameters"])
def filter_items(
    category: str = Query(
        ...,  # Required
        min_length=2,
        max_length=30,
        pattern="^[a-zA-Z]+$"
    ),
    in_stock: bool = Query(True),
    tags: List[str] = Query(
        [],
        min_length=1,
        max_length=20,
        description="List of tags to filter by"
    )
):
    """
    Filter endpoint demonstrating required queries and list parameters
    
    Example: /filter?category=electronics&in_stock=true&tags=new&tags=sale
    """
    return {
        "category": category,
        "in_stock": in_stock,
        "tags": tags
    }

# ==================== Path Parameter Validation ====================

@app.get("/users/{user_id}", tags=["Path Parameters"])
def get_user(
    user_id: Annotated[int, Path(
        ge=1,
        le=999999,
        description="User ID (1-999999)"
    )]
):
    """
    Get user by ID with path parameter validation
    
    Example: /users/12345
    """
    return {"user_id": user_id, "message": f"Fetching user {user_id}"}

@app.get("/products/{sku}", tags=["Path Parameters"])
def get_product(
    sku: Annotated[str, Path(
        min_length=7,
        max_length=7,
        pattern="^[A-Z]{3}-\\d{4}$",
        description="Product SKU (format: ABC-1234)"
    )]
):
    """
    Get product by SKU with regex validation
    
    Example: /products/LAP-1234
    """
    return {"sku": sku, "message": f"Fetching product {sku}"}

@app.get("/orders/{year}/{month}/{order_id}", tags=["Path Parameters"])
def get_order(
    year: Annotated[int, Path(ge=2020, le=2030, description="Year (2020-2030)")],
    month: Annotated[int, Path(ge=1, le=12, description="Month (1-12)")],
    order_id: Annotated[str, Path(
        pattern="^ORD-[A-Z0-9]{8}$",
        description="Order ID (format: ORD-XXXXXXXX)"
    )]
):
    """
    Get order with multiple validated path parameters
    
    Example: /orders/2024/12/ORD-ABC12345
    """
    return {
        "year": year,
        "month": month,
        "order_id": order_id,
        "message": f"Fetching order {order_id} from {month}/{year}"
    }

# ==================== Body Parameter Validation ====================

@app.post("/users", tags=["Body Parameters"])
def create_user(user: User):
    """
    Create user with validated Pydantic model
    
    All validations are defined in the User model:
    - username: 3-20 chars, alphanumeric + underscore
    - email: valid email format
    - age: 18-120
    - phone: optional, E.164 format
    - bio: optional, max 500 chars
    """
    return {
        "message": "User created successfully",
        "user": user
    }

@app.post("/products", tags=["Body Parameters"])
def create_product(product: Product):
    """
    Create product with numeric and regex validation
    
    Example body:
    {
        "name": "Laptop",
        "price": 999.99,
        "quantity": 50,
        "discount": 10,
        "sku": "LAP-1234"
    }
    """
    return {
        "message": "Product created successfully",
        "product": product
    }

@app.post("/reviews", tags=["Body Parameters"])
def create_review(review: Review):
    """
    Create review with custom validation
    
    Includes custom validator to prevent spam words
    """
    return {
        "message": "Review created successfully",
        "review": review
    }

# ==================== Mixed Parameters (Path, Query, Body) ====================

@app.put("/users/{user_id}", tags=["Mixed Parameters"])
def update_user(
    user_id: Annotated[int, Path(ge=1, description="User ID")],
    user: User,
    send_email: Annotated[bool, Query(description="Send confirmation email")] = False
):
    """
    Update user combining path parameter, body, and query parameter
    
    Example: PUT /users/123?send_email=true
    """
    return {
        "message": f"User {user_id} updated successfully",
        "send_email": send_email,
        "updated_user": user
    }

@app.post("/products/{product_id}/reviews", tags=["Mixed Parameters"])
def add_product_review(
    product_id: Annotated[int, Path(ge=1, description="Product ID")],
    review: Review,
    verified_purchase: Annotated[bool, Query(description="Is verified purchase?")] = False
):
    """
    Add review to product with mixed parameter validation
    
    Example: POST /products/456/reviews?verified_purchase=true
    """
    return {
        "message": f"Review added to product {product_id}",
        "verified_purchase": verified_purchase,
        "review": review
    }

# ==================== Body() with Multiple Parameters ====================

@app.post("/items/complex", tags=["Body Parameters"])
def create_complex_item(
    product: Annotated[Product, Body(embed=True)],
    user: Annotated[User, Body(embed=True)],
    quantity: Annotated[int, Body(ge=1, le=1000, embed=True)],
    notes: Annotated[Optional[str], Body(max_length=500)] = None
):
    """
    Create item with multiple body parameters
    
    Example body:
    {
        "product": { ... },
        "user": { ... },
        "quantity": 5,
        "notes": "Special instructions"
    }
    """
    return {
        "message": "Complex item created",
        "product": product,
        "user": user,
        "quantity": quantity,
        "notes": notes
    }

@app.post("/orders/place", tags=["Body Parameters"])
def place_order(
    product_id: Annotated[int, Body(ge=1)],
    quantity: Annotated[int, Body(ge=1, le=100)],
    priority: Annotated[str, Body(pattern="^(low|medium|high|urgent)$")],
    discount_code: Annotated[Optional[str], Body(
        pattern="^[A-Z0-9]{6,10}$",
        description="Discount code (6-10 uppercase alphanumeric)"
    )] = None
):
    """
    Place order with individual body parameters
    
    Example body:
    {
        "product_id": 123,
        "quantity": 5,
        "priority": "high",
        "discount_code": "SAVE10"
    }
    """
    return {
        "message": "Order placed successfully",
        "product_id": product_id,
        "quantity": quantity,
        "priority": priority,
        "discount_code": discount_code
    }

# ==================== Advanced Validation Examples ====================

@app.get("/advanced/regex-examples", tags=["Advanced"])
def regex_examples(
    ip_address: Annotated[Optional[str], Query(
        pattern="^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$",
        description="IPv4 address format"
    )] = None,
    hex_color: Annotated[Optional[str], Query(
        pattern="^#[0-9A-Fa-f]{6}$",
        description="Hex color code (e.g., #FF5733)"
    )] = None,
    url_slug: Annotated[Optional[str], Query(
        pattern="^[a-z0-9]+(?:-[a-z0-9]+)*$",
        description="URL slug (lowercase, hyphens allowed)"
    )] = None,
    credit_card: Annotated[Optional[str], Query(
        pattern="^\\d{4}-\\d{4}-\\d{4}-\\d{4}$",
        description="Credit card (format: 1234-5678-9012-3456)"
    )] = None
):
    """
    Advanced regex validation examples
    
    Examples:
    - /advanced/regex-examples?ip_address=192.168.1.1
    - /advanced/regex-examples?hex_color=#FF5733
    - /advanced/regex-examples?url_slug=my-product-name
    - /advanced/regex-examples?credit_card=1234-5678-9012-3456
    """
    return {
        "ip_address": ip_address,
        "hex_color": hex_color,
        "url_slug": url_slug,
        "credit_card": credit_card if credit_card else "Not provided"
    }

@app.post("/advanced/nested-validation", tags=["Advanced"])
def nested_validation(
    name: Annotated[str, Body(min_length=1, max_length=100)],
    price: Annotated[float, Body(gt=0, le=1000000)],
    metadata: Annotated[dict, Body(description="Additional metadata")] = {}
):
    """
    Endpoint with nested validation
    
    Example body:
    {
        "name": "Product Name",
        "price": 99.99,
        "metadata": {
            "category": "Electronics",
            "brand": "BrandX"
        }
    }
    """
    return {
        "name": name,
        "price": price,
        "metadata": metadata
    }

# ==================== Root and Health ====================

@app.get("/", tags=["Root"])
def read_root():
    """
    Welcome endpoint with API documentation links
    """
    return {
        "message": "Request Validation API",
        "docs": "/docs",
        "redoc": "/redoc",
        "examples": {
            "query_params": "/search?q=laptop&page=1&limit=10",
            "path_params": "/products/LAP-1234",
            "body_params": "POST /users with JSON body"
        }
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "api": "Request Validation Examples"}

# ==================== Example Usage ====================
"""
TESTING EXAMPLES:

1. Query Parameter Validation:
   curl "http://localhost:8000/search?q=laptop&page=1&limit=20&min_price=100&max_price=1000"

2. Path Parameter Validation:
   curl "http://localhost:8000/products/LAP-1234"

3. Body Parameter Validation:
   curl -X POST "http://localhost:8000/users" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "john_doe",
       "email": "john@example.com",
       "age": 25,
       "phone": "+12125551234",
       "bio": "Software developer"
     }'

4. Mixed Parameters:
   curl -X PUT "http://localhost:8000/users/123?send_email=true" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "jane_doe",
       "email": "jane@example.com",
       "age": 30
     }'

5. Regex Validation:
   curl "http://localhost:8000/advanced/regex-examples?hex_color=%23FF5733&url_slug=my-product"

Run the app with: uvicorn 02_request_validation:app --reload
"""
