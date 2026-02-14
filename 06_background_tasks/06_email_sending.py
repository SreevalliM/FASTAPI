"""
FastAPI Background Tasks - Email Sending Example
================================================

This module demonstrates realistic email sending scenarios using background tasks.

Features:
- User registration with welcome email
- Password reset emails
- Order confirmation emails
- Newsletter subscription
- Bulk email sending

Note: This uses simulated email sending. In production, use services like:
- SendGrid
- AWS SES
- Mailgun
- SMTP
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import asyncio
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI(title="Email Background Tasks API")

# Models
class UserRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class OrderConfirmation(BaseModel):
    order_id: str
    email: EmailStr
    items: List[str]
    total: float

class NewsletterSubscription(BaseModel):
    email: EmailStr
    preferences: Optional[List[str]] = None

class BulkEmailRequest(BaseModel):
    recipients: List[EmailStr]
    subject: str
    body: str

# In-memory storage for demo
email_logs = []
users_db = {}

# ========================================
# Email Sending Functions (Simulated)
# ========================================

async def send_email_async(
    to_email: str,
    subject: str,
    body: str,
    email_type: str = "notification"
):
    """
    Asynchronous email sending (simulated)
    
    In production, replace this with:
    - SMTP client (aiosmtplib)
    - SendGrid API
    - AWS SES
    - Mailgun
    """
    # Simulate email sending delay
    await asyncio.sleep(2)
    
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "to": to_email,
        "subject": subject,
        "body": body,
        "type": email_type,
        "status": "sent"
    }
    email_logs.append(log_entry)
    
    print(f"\n📧 EMAIL SENT")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body}\n")
    
    return True

def send_email_sync(
    to_email: str,
    subject: str,
    body: str,
    email_type: str = "notification"
):
    """
    Synchronous email sending (simulated)
    Use for traditional SMTP libraries
    """
    import time
    time.sleep(2)
    
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "to": to_email,
        "subject": subject,
        "body": body,
        "type": email_type,
        "status": "sent"
    }
    email_logs.append(log_entry)
    
    print(f"\n📧 EMAIL SENT (SYNC)")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body}\n")
    
    return True

# ========================================
# Real SMTP Example (Commented Out)
# ========================================

async def send_real_email_smtp(
    to_email: str,
    subject: str,
    body: str,
    from_email: str = "noreply@example.com",
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 587,
    smtp_username: str = "",
    smtp_password: str = ""
):
    """
    Real SMTP email sending example
    
    Uncomment and configure with your SMTP credentials to use
    """
    # Uncomment to use real SMTP
    """
    try:
        message = MIMEMultipart()
        message["From"] = from_email
        message["To"] = to_email
        message["Subject"] = subject
        
        message.attach(MIMEText(body, "plain"))
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        
        # Send email
        server.send_message(message)
        server.quit()
        
        print(f"✅ Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        return False
    """
    pass

# ========================================
# Email Template Functions
# ========================================

def get_welcome_email_body(username: str, full_name: str) -> str:
    """Generate welcome email body"""
    return f"""
Hello {full_name},

Welcome to our platform! We're excited to have you on board.

Your username: {username}

Get started by exploring our features and setting up your profile.

Best regards,
The Team
"""

def get_password_reset_email_body(reset_token: str) -> str:
    """Generate password reset email body"""
    return f"""
You requested to reset your password.

Use this token to reset your password: {reset_token}

This token will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
The Team
"""

def get_order_confirmation_body(order_id: str, items: List[str], total: float) -> str:
    """Generate order confirmation email body"""
    items_list = "\n".join([f"- {item}" for item in items])
    return f"""
Thank you for your order!

Order ID: {order_id}

Items:
{items_list}

Total: ${total:.2f}

Your order is being processed and will be shipped soon.

Best regards,
The Team
"""

# ========================================
# API Endpoints
# ========================================

@app.post("/register")
async def register_user(
    user: UserRegistration,
    background_tasks: BackgroundTasks
):
    """
    User registration with welcome email sent in background
    """
    # Check if user already exists
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Save user
    users_db[user.email] = {
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "created_at": datetime.now().isoformat()
    }
    
    # Send welcome email in background
    email_body = get_welcome_email_body(user.username, user.full_name)
    background_tasks.add_task(
        send_email_async,
        user.email,
        "Welcome to Our Platform!",
        email_body,
        "welcome"
    )
    
    return {
        "message": "User registered successfully",
        "username": user.username,
        "email": user.email,
        "note": "Welcome email will be sent shortly"
    }

@app.post("/password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks
):
    """
    Password reset request with email sent in background
    """
    # Check if user exists
    if request.email not in users_db:
        # Don't reveal if email exists or not (security best practice)
        return {
            "message": "If the email exists, a password reset link will be sent"
        }
    
    # Generate reset token (in production, use proper token generation)
    reset_token = f"RESET_{request.email}_{datetime.now().timestamp()}"
    
    # Send password reset email in background
    email_body = get_password_reset_email_body(reset_token)
    background_tasks.add_task(
        send_email_async,
        request.email,
        "Password Reset Request",
        email_body,
        "password_reset"
    )
    
    return {
        "message": "If the email exists, a password reset link will be sent",
        "note": "Check your email for instructions"
    }

@app.post("/order-confirmation")
async def send_order_confirmation(
    order: OrderConfirmation,
    background_tasks: BackgroundTasks
):
    """
    Send order confirmation email in background
    """
    email_body = get_order_confirmation_body(order.order_id, order.items, order.total)
    
    background_tasks.add_task(
        send_email_async,
        order.email,
        f"Order Confirmation - {order.order_id}",
        email_body,
        "order_confirmation"
    )
    
    return {
        "message": "Order confirmed",
        "order_id": order.order_id,
        "total": order.total,
        "note": "Confirmation email will be sent shortly"
    }

@app.post("/subscribe-newsletter")
async def subscribe_newsletter(
    subscription: NewsletterSubscription,
    background_tasks: BackgroundTasks
):
    """
    Newsletter subscription with confirmation email
    """
    email_body = f"""
Thank you for subscribing to our newsletter!

You'll receive updates about:
{', '.join(subscription.preferences) if subscription.preferences else 'All topics'}

You can unsubscribe at any time.

Best regards,
The Team
"""
    
    background_tasks.add_task(
        send_email_async,
        subscription.email,
        "Newsletter Subscription Confirmed",
        email_body,
        "newsletter"
    )
    
    return {
        "message": "Subscribed successfully",
        "email": subscription.email,
        "preferences": subscription.preferences
    }

@app.post("/bulk-email")
async def send_bulk_email(
    bulk_request: BulkEmailRequest,
    background_tasks: BackgroundTasks
):
    """
    Send bulk emails in background
    
    Each email is sent as a separate background task
    """
    if len(bulk_request.recipients) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 recipients allowed per bulk send"
        )
    
    # Add a background task for each recipient
    for recipient in bulk_request.recipients:
        background_tasks.add_task(
            send_email_async,
            recipient,
            bulk_request.subject,
            bulk_request.body,
            "bulk"
        )
    
    return {
        "message": "Bulk email queued",
        "recipients_count": len(bulk_request.recipients),
        "note": "Emails will be sent in the background"
    }

# ========================================
# Utility Endpoints
# ========================================

@app.get("/email-logs")
async def get_email_logs(limit: int = 20):
    """Get recent email logs"""
    return {
        "total_emails": len(email_logs),
        "logs": email_logs[-limit:]
    }

@app.get("/email-logs/{email}")
async def get_user_email_logs(email: str):
    """Get email logs for specific email address"""
    user_logs = [log for log in email_logs if log["to"] == email]
    return {
        "email": email,
        "total_emails": len(user_logs),
        "logs": user_logs
    }

@app.delete("/email-logs")
async def clear_email_logs():
    """Clear all email logs"""
    email_logs.clear()
    return {"message": "Email logs cleared"}

@app.get("/users")
async def list_users():
    """List registered users"""
    return {
        "total_users": len(users_db),
        "users": list(users_db.values())
    }

@app.get("/")
async def root():
    return {
        "message": "Email Background Tasks API",
        "endpoints": {
            "register": "POST /register",
            "password_reset": "POST /password-reset",
            "order_confirmation": "POST /order-confirmation",
            "subscribe_newsletter": "POST /subscribe-newsletter",
            "bulk_email": "POST /bulk-email",
            "email_logs": "GET /email-logs",
            "users": "GET /users"
        },
        "note": "All emails are sent in the background using BackgroundTasks"
    }

# ========================================
# Run the app
# ========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
