"""
CORS (Cross-Origin Resource Sharing) Middleware

This module demonstrates CORS configuration patterns:
- Basic CORS setup
- Secure CORS configuration
- Development vs Production CORS
- Preflight request handling
- Multiple origin patterns
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from typing import List
import os

# ============================================================================
# BASIC CORS CONFIGURATION
# ============================================================================

app_basic = FastAPI(
    title="Basic CORS API",
    version="1.0.0",
    description="Simple CORS configuration allowing all origins"
)

# WARNING: Only use this in development!
# This allows ALL origins, methods, and headers
app_basic.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when allow_origins is ["*"]
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app_basic.get("/")
async def basic_root():
    return {
        "message": "Basic CORS API",
        "cors_policy": "Allow all origins (development only!)"
    }


@app_basic.get("/data")
async def basic_data():
    return {
        "data": ["item1", "item2", "item3"],
        "accessible": "from any origin"
    }


# ============================================================================
# SECURE CORS CONFIGURATION
# ============================================================================

app_secure = FastAPI(
    title="Secure CORS API",
    version="1.0.0",
    description="Production-ready CORS with specific origins"
)

# Production-ready CORS configuration
# Only allow specific trusted origins
allowed_origins = [
    "https://myapp.com",
    "https://www.myapp.com",
    "https://app.myapp.com",
    "http://localhost:3000",  # React development
    "http://localhost:8080",  # Vue development
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
]

app_secure.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Specific methods only
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "X-Requested-With",
    ],
    expose_headers=[
        "X-Total-Count",
        "X-Page-Number",
        "X-Request-ID",
    ],
    max_age=600,  # Cache preflight requests for 10 minutes
)


@app_secure.get("/")
async def secure_root():
    return {
        "message": "Secure CORS API",
        "cors_policy": "Only specific origins allowed",
        "allowed_origins": allowed_origins
    }


@app_secure.get("/protected-data")
async def protected_data():
    return {
        "data": "This is protected data",
        "note": "Only accessible from allowed origins"
    }


@app_secure.post("/submit")
async def submit_data(data: dict):
    return {
        "message": "Data received",
        "received": data,
        "note": "POST requests require CORS preflight"
    }


# ============================================================================
# ENVIRONMENT-BASED CORS
# ============================================================================

app_env = FastAPI(
    title="Environment-Based CORS API",
    version="1.0.0",
    description="CORS configuration that changes based on environment"
)

# Determine environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    # Strict CORS for production
    cors_origins = [
        "https://myapp.com",
        "https://www.myapp.com",
    ]
    allow_credentials = True
    allow_methods = ["GET", "POST", "PUT", "DELETE"]
    
elif ENVIRONMENT == "staging":
    # Moderate CORS for staging
    cors_origins = [
        "https://staging.myapp.com",
        "https://dev.myapp.com",
        "http://localhost:3000",
    ]
    allow_credentials = True
    allow_methods = ["*"]
    
else:  # development
    # Permissive CORS for development
    cors_origins = ["*"]
    allow_credentials = False
    allow_methods = ["*"]

app_env.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=allow_methods,
    allow_headers=["*"],
)


@app_env.get("/")
async def env_root():
    return {
        "message": "Environment-Based CORS API",
        "environment": ENVIRONMENT,
        "cors_policy": "Automatically configured based on environment"
    }


@app_env.get("/config")
async def get_config():
    return {
        "environment": ENVIRONMENT,
        "allowed_origins": cors_origins if cors_origins != ["*"] else "all",
        "allows_credentials": allow_credentials,
    }


# ============================================================================
# PATTERN-BASED CORS (With Custom Middleware)
# ============================================================================

app_pattern = FastAPI(
    title="Pattern-Based CORS API",
    version="1.0.0",
    description="CORS with regex pattern matching for origins"
)

import re
from typing import Sequence
from starlette.middleware.cors import ALL_METHODS
from starlette.types import ASGIApp


class CustomCORSMiddleware(CORSMiddleware):
    """
    Custom CORS middleware that supports regex patterns.
    """
    def __init__(
        self,
        app: ASGIApp,
        allow_origin_patterns: List[str] = None,
        **kwargs
    ):
        super().__init__(app, **kwargs)
        self.allow_origin_patterns = [
            re.compile(pattern) for pattern in (allow_origin_patterns or [])
        ]
    
    def is_allowed_origin(self, origin: str) -> bool:
        # Check exact matches first
        if origin in self.allow_origins:
            return True
        
        # Check pattern matches
        for pattern in self.allow_origin_patterns:
            if pattern.match(origin):
                return True
        
        # Check wildcard
        if "*" in self.allow_origins:
            return True
        
        return False


# Add custom CORS middleware with patterns
app_pattern.add_middleware(
    CustomCORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
    ],
    allow_origin_patterns=[
        r"https://.*\.myapp\.com",  # All subdomains of myapp.com
        r"https://.*\.example\.com",  # All subdomains of example.com
        r"http://localhost:\d+",  # Any localhost port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app_pattern.get("/")
async def pattern_root():
    return {
        "message": "Pattern-Based CORS API",
        "cors_policy": "Supports regex patterns for origins",
        "examples": [
            "https://*.myapp.com",
            "https://*.example.com",
            "http://localhost:*"
        ]
    }


# ============================================================================
# CORS WITH PREFLIGHT TESTING
# ============================================================================

app_preflight = FastAPI(
    title="CORS Preflight Testing API",
    version="1.0.0",
    description="API for testing CORS preflight requests"
)

app_preflight.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Custom-Header"],
    max_age=3600,  # 1 hour
)


@app_preflight.get("/")
async def preflight_root(request: Request):
    return {
        "message": "CORS Preflight Testing API",
        "origin": request.headers.get("origin", "No origin header"),
        "tip": "Use browser DevTools to see preflight OPTIONS requests"
    }


@app_preflight.get("/simple")
async def simple_cors_request():
    """
    Simple CORS request (GET) - No preflight needed.
    """
    return {
        "type": "simple_request",
        "note": "GET requests usually don't trigger preflight"
    }


@app_preflight.post("/complex")
async def complex_cors_request(data: dict):
    """
    Complex CORS request (POST with JSON) - Triggers preflight.
    
    Browser will send OPTIONS request first, then POST.
    """
    return {
        "type": "complex_request",
        "note": "POST with Content-Type: application/json triggers preflight",
        "received": data
    }


@app_preflight.put("/update/{item_id}")
async def update_item(item_id: int, data: dict):
    """
    PUT request - Always triggers preflight.
    """
    return {
        "type": "preflight_required",
        "method": "PUT",
        "item_id": item_id,
        "updated": data
    }


@app_preflight.delete("/delete/{item_id}")
async def delete_item(item_id: int):
    """
    DELETE request - Always triggers preflight.
    """
    return {
        "type": "preflight_required",
        "method": "DELETE",
        "item_id": item_id,
        "status": "deleted"
    }


@app_preflight.get("/with-custom-header")
async def custom_header():
    """
    Response with custom header that needs to be exposed.
    """
    from fastapi.responses import JSONResponse
    
    content = {
        "message": "Check the X-Custom-Header",
        "note": "Custom headers must be listed in expose_headers"
    }
    
    headers = {
        "X-Custom-Header": "This is a custom header value"
    }
    
    return JSONResponse(content=content, headers=headers)


# ============================================================================
# CORS TEST HTML PAGE
# ============================================================================

@app_preflight.get("/test-page", response_class=HTMLResponse)
async def test_page():
    """
    HTML page for manual CORS testing.
    """
    from fastapi.responses import HTMLResponse
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CORS Test Page</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            button { margin: 10px; padding: 10px; }
            #output { 
                margin-top: 20px; 
                padding: 10px; 
                background: #f0f0f0; 
                border-radius: 5px;
                white-space: pre-wrap;
            }
        </style>
    </head>
    <body>
        <h1>CORS Testing</h1>
        <p>Open browser DevTools (Network tab) to see CORS headers</p>
        
        <button onclick="testSimple()">Test Simple GET</button>
        <button onclick="testComplex()">Test Complex POST</button>
        <button onclick="testPUT()">Test PUT (Preflight)</button>
        <button onclick="testDELETE()">Test DELETE (Preflight)</button>
        <button onclick="testCustomHeader()">Test Custom Header</button>
        
        <div id="output">Results will appear here...</div>
        
        <script>
            const API_URL = window.location.origin;
            const output = document.getElementById('output');
            
            async function testSimple() {
                try {
                    const response = await fetch(API_URL + '/simple');
                    const data = await response.json();
                    output.textContent = 'Simple GET:\\n' + JSON.stringify(data, null, 2);
                } catch (error) {
                    output.textContent = 'Error: ' + error.message;
                }
            }
            
            async function testComplex() {
                try {
                    const response = await fetch(API_URL + '/complex', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ test: 'data' })
                    });
                    const data = await response.json();
                    output.textContent = 'Complex POST:\\n' + JSON.stringify(data, null, 2);
                } catch (error) {
                    output.textContent = 'Error: ' + error.message;
                }
            }
            
            async function testPUT() {
                try {
                    const response = await fetch(API_URL + '/update/123', {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name: 'Updated' })
                    });
                    const data = await response.json();
                    output.textContent = 'PUT Request:\\n' + JSON.stringify(data, null, 2);
                } catch (error) {
                    output.textContent = 'Error: ' + error.message;
                }
            }
            
            async function testDELETE() {
                try {
                    const response = await fetch(API_URL + '/delete/123', {
                        method: 'DELETE'
                    });
                    const data = await response.json();
                    output.textContent = 'DELETE Request:\\n' + JSON.stringify(data, null, 2);
                } catch (error) {
                    output.textContent = 'Error: ' + error.message;
                }
            }
            
            async function testCustomHeader() {
                try {
                    const response = await fetch(API_URL + '/with-custom-header');
                    const data = await response.json();
                    const customHeader = response.headers.get('X-Custom-Header');
                    output.textContent = 'Custom Header Response:\\n' + 
                        JSON.stringify(data, null, 2) + 
                        '\\n\\nX-Custom-Header: ' + customHeader;
                } catch (error) {
                    output.textContent = 'Error: ' + error.message;
                }
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


# ============================================================================
# MAIN APPLICATION (Combined)
# ============================================================================

app = FastAPI(
    title="CORS Middleware Examples",
    version="1.0.0",
    description="Comprehensive CORS configuration examples"
)

# Mount sub-applications
app.mount("/basic", app_basic)
app.mount("/secure", app_secure)
app.mount("/env", app_env)
app.mount("/pattern", app_pattern)
app.mount("/preflight", app_preflight)


@app.get("/")
async def root():
    return {
        "message": "CORS Middleware Examples",
        "examples": {
            "basic": "/basic - Allow all origins (dev only)",
            "secure": "/secure - Production-ready CORS",
            "env": "/env - Environment-based configuration",
            "pattern": "/pattern - Pattern matching origins",
            "preflight": "/preflight - Preflight testing"
        },
        "test_page": "/preflight/test-page",
        "docs": "/docs"
    }


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting CORS Middleware Examples API...")
    print("\n📘 CORS Configurations Available:")
    print("  /basic     - Basic CORS (allow all)")
    print("  /secure    - Secure CORS (specific origins)")
    print("  /env       - Environment-based CORS")
    print("  /pattern   - Pattern-based CORS")
    print("  /preflight - Preflight testing")
    print("\n🧪 Test CORS:")
    print("  http://localhost:8003/preflight/test-page")
    print("\n📚 Documentation:")
    print("  http://localhost:8003/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8003)
