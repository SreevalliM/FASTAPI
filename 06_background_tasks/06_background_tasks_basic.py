"""
FastAPI Background Tasks - Basic Examples
==========================================

This module demonstrates:
1. Basic BackgroundTasks usage
2. Multiple background tasks
3. Sync vs Async background tasks
4. Background tasks with dependencies
"""

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional
import time
import asyncio
from datetime import datetime

app = FastAPI(title="Background Tasks API")

# Models
class NotificationRequest(BaseModel):
    email: EmailStr
    message: str

class OrderRequest(BaseModel):
    item: str
    quantity: int
    email: EmailStr

# In-memory log storage (for demonstration)
task_logs = []

# ========================================
# SYNC Background Task Functions
# ========================================

def write_log(message: str):
    """Synchronous background task - writes to log"""
    time.sleep(2)  # Simulate slow operation
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] {message}"
    task_logs.append(log_entry)
    print(f"✅ Log written: {log_entry}")

def send_notification(email: str, message: str):
    """Synchronous background task - simulates sending notification"""
    time.sleep(3)  # Simulate email sending delay
    timestamp = datetime.now().isoformat()
    log = f"[{timestamp}] Notification sent to {email}: {message}"
    task_logs.append(log)
    print(f"📧 {log}")

def process_order(item: str, quantity: int):
    """Synchronous background task - processes order"""
    time.sleep(2)
    timestamp = datetime.now().isoformat()
    log = f"[{timestamp}] Processed order: {quantity}x {item}"
    task_logs.append(log)
    print(f"📦 {log}")

# ========================================
# ASYNC Background Task Functions
# ========================================

async def async_write_log(message: str):
    """Asynchronous background task - writes to log"""
    await asyncio.sleep(2)
    timestamp = datetime.now().isoformat()
    log_entry = f"[{timestamp}] ASYNC: {message}"
    task_logs.append(log_entry)
    print(f"✅ Async log written: {log_entry}")

async def async_send_notification(email: str, message: str):
    """Asynchronous background task - simulates sending notification"""
    await asyncio.sleep(3)
    timestamp = datetime.now().isoformat()
    log = f"[{timestamp}] ASYNC Notification sent to {email}: {message}"
    task_logs.append(log)
    print(f"📧 {log}")

async def async_process_order(item: str, quantity: int):
    """Asynchronous background task - processes order"""
    await asyncio.sleep(2)
    timestamp = datetime.now().isoformat()
    log = f"[{timestamp}] ASYNC Processed order: {quantity}x {item}"
    task_logs.append(log)
    print(f"📦 {log}")

# ========================================
# API Endpoints - Basic Background Tasks
# ========================================

@app.post("/simple/notification")
async def simple_notification(
    notification: NotificationRequest,
    background_tasks: BackgroundTasks
):
    """
    Simple example: Add a single background task
    Response returns immediately, task runs in background
    """
    background_tasks.add_task(send_notification, notification.email, notification.message)
    
    return {
        "message": "Notification queued successfully",
        "email": notification.email,
        "status": "processing"
    }

@app.post("/simple/notification-async")
async def simple_notification_async(
    notification: NotificationRequest,
    background_tasks: BackgroundTasks
):
    """
    Async background task example
    """
    background_tasks.add_task(async_send_notification, notification.email, notification.message)
    
    return {
        "message": "Async notification queued successfully",
        "email": notification.email,
        "status": "processing"
    }

# ========================================
# Multiple Background Tasks
# ========================================

@app.post("/order")
async def create_order(
    order: OrderRequest,
    background_tasks: BackgroundTasks
):
    """
    Multiple background tasks example
    
    When an order is created:
    1. Process the order
    2. Send confirmation email
    3. Write to log
    
    All three tasks run in the background, response returns immediately
    """
    # Add multiple background tasks
    background_tasks.add_task(process_order, order.item, order.quantity)
    background_tasks.add_task(
        send_notification, 
        order.email, 
        f"Your order for {order.quantity}x {order.item} has been received"
    )
    background_tasks.add_task(
        write_log, 
        f"New order from {order.email}: {order.quantity}x {order.item}"
    )
    
    return {
        "message": "Order created successfully",
        "order": {
            "item": order.item,
            "quantity": order.quantity,
            "email": order.email
        },
        "status": "processing",
        "note": "You will receive a confirmation email shortly"
    }

@app.post("/order-async")
async def create_order_async(
    order: OrderRequest,
    background_tasks: BackgroundTasks
):
    """
    Multiple ASYNC background tasks
    Async tasks are more efficient for I/O-bound operations
    """
    background_tasks.add_task(async_process_order, order.item, order.quantity)
    background_tasks.add_task(
        async_send_notification, 
        order.email, 
        f"Your order for {order.quantity}x {order.item} has been received"
    )
    background_tasks.add_task(
        async_write_log, 
        f"New order from {order.email}: {order.quantity}x {order.item}"
    )
    
    return {
        "message": "Order created successfully (async processing)",
        "order": {
            "item": order.item,
            "quantity": order.quantity,
            "email": order.email
        },
        "status": "processing"
    }

# ========================================
# Utility Endpoints
# ========================================

@app.get("/logs")
async def get_logs():
    """Get all background task logs"""
    return {
        "total_logs": len(task_logs),
        "logs": task_logs[-20:]  # Return last 20 logs
    }

@app.delete("/logs")
async def clear_logs():
    """Clear all logs"""
    task_logs.clear()
    return {"message": "Logs cleared"}

@app.get("/")
async def root():
    return {
        "message": "Background Tasks API",
        "endpoints": {
            "simple_notification": "POST /simple/notification",
            "simple_notification_async": "POST /simple/notification-async",
            "create_order": "POST /order",
            "create_order_async": "POST /order-async",
            "get_logs": "GET /logs",
            "clear_logs": "DELETE /logs"
        },
        "note": "All tasks run in the background - responses return immediately"
    }

# ========================================
# Run the app
# ========================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
