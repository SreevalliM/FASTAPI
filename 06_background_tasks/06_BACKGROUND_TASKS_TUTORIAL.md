# FastAPI Background Tasks - Complete Tutorial

## Table of Contents
1. [Introduction](#introduction)
2. [What are Background Tasks?](#what-are-background-tasks)
3. [Basic Usage](#basic-usage)
4. [Async vs Sync Tasks](#async-vs-sync-tasks)
5. [Multiple Background Tasks](#multiple-background-tasks)
6. [Email Sending Example](#email-sending-example)
7. [Best Practices](#best-practices)
8. [Common Pitfalls](#common-pitfalls)
9. [When NOT to Use Background Tasks](#when-not-to-use-background-tasks)
10. [Production Alternatives](#production-alternatives)

---

## Introduction

Background Tasks in FastAPI allow you to run functions **after** returning a response to the client. This is perfect for operations that:
- Don't need to complete before sending the response
- Would slow down the response time if executed synchronously
- Are fire-and-forget operations

**Key Benefit:** The client doesn't have to wait for these tasks to complete.

---

## What are Background Tasks?

Background tasks are functions that run **after** the response is sent to the client but **before** the application shuts down.

### Perfect Use Cases
✅ Sending emails  
✅ Processing uploaded files  
✅ Generating reports  
✅ Logging to external services  
✅ Cleaning up resources  
✅ Triggering webhooks  
✅ Updating cache  

### NOT Suitable For
❌ Long-running tasks (> 1 minute)  
❌ Tasks that must be guaranteed to complete  
❌ Heavy computational work  
❌ Tasks requiring retry logic  
❌ Scheduled/periodic tasks  

---

## Basic Usage

### Step 1: Import BackgroundTasks

```python
from fastapi import FastAPI, BackgroundTasks
```

### Step 2: Define Your Background Function

```python
def write_log(message: str):
    """This function will run in the background"""
    with open("log.txt", "a") as f:
        f.write(f"{message}\n")
```

### Step 3: Use in Endpoint

```python
@app.post("/send-notification")
async def send_notification(
    email: str,
    background_tasks: BackgroundTasks  # Inject dependency
):
    # Add task to background tasks queue
    background_tasks.add_task(write_log, f"Notification sent to {email}")
    
    # Response is sent immediately!
    return {"message": "Notification sent"}
```

### How It Works

1. Client makes request → `/send-notification`
2. FastAPI processes request
3. Task added to queue via `background_tasks.add_task()`
4. **Response sent immediately** to client
5. Background task executes **after** response is sent
6. Client is already free to continue

---

## Async vs Sync Tasks

FastAPI supports both synchronous and asynchronous background tasks.

### Synchronous Tasks

Use `def` for:
- CPU-bound operations
- Blocking I/O operations
- Traditional libraries (non-async)

```python
def sync_task(data: str):
    """Synchronous background task"""
    import time
    time.sleep(5)  # Blocking
    print(f"Processed: {data}")

@app.post("/sync-example")
async def sync_example(background_tasks: BackgroundTasks):
    background_tasks.add_task(sync_task, "Hello")
    return {"message": "Task queued"}
```

**How it runs:** In a thread pool

### Asynchronous Tasks

Use `async def` for:
- I/O-bound operations
- Network requests
- Database queries
- File I/O (with async libraries)

```python
async def async_task(data: str):
    """Asynchronous background task"""
    import asyncio
    await asyncio.sleep(5)  # Non-blocking
    print(f"Processed: {data}")

@app.post("/async-example")
async def async_example(background_tasks: BackgroundTasks):
    background_tasks.add_task(async_task, "Hello")
    return {"message": "Task queued"}
```

**How it runs:** In the event loop (more efficient)

### Which Should You Use?

| Operation Type | Use | Example |
|----------------|-----|---------|
| Network request (HTTP, API) | `async def` | Calling external API |
| Database query (async driver) | `async def` | SQLAlchemy async |
| Email sending (async client) | `async def` | aiosmtplib |
| File I/O (async) | `async def` | aiofiles |
| CPU-intensive task | `def` | Data processing |
| Traditional blocking library | `def` | smtplib |

**General Rule:** Prefer `async def` for better performance with I/O operations.

---

## Multiple Background Tasks

You can add multiple background tasks to the same request. They execute **in the order they were added**.

```python
def task_one(name: str):
    print(f"Task 1: {name}")
    time.sleep(2)

def task_two(name: str):
    print(f"Task 2: {name}")
    time.sleep(2)

def task_three(name: str):
    print(f"Task 3: {name}")
    time.sleep(2)

@app.post("/multiple-tasks")
async def multiple_tasks(background_tasks: BackgroundTasks):
    # Add multiple tasks
    background_tasks.add_task(task_one, "First")
    background_tasks.add_task(task_two, "Second")
    background_tasks.add_task(task_three, "Third")
    
    return {"message": "3 tasks queued"}
```

**Execution:**
1. Response sent immediately
2. `task_one` runs (2 seconds)
3. `task_two` runs (2 seconds)
4. `task_three` runs (2 seconds)
5. Total: ~6 seconds after response

**Important:** Tasks run sequentially, not in parallel!

### Running Tasks in Parallel

If you need parallel execution, use `async` tasks:

```python
async def parallel_task(name: str):
    await asyncio.sleep(2)
    print(f"Task: {name}")

@app.post("/parallel")
async def parallel_example(background_tasks: BackgroundTasks):
    # These will run concurrently if they await I/O
    background_tasks.add_task(parallel_task, "One")
    background_tasks.add_task(parallel_task, "Two")
    background_tasks.add_task(parallel_task, "Three")
    
    return {"message": "Tasks queued"}
```

---

## Email Sending Example

One of the most common use cases for background tasks is sending emails.

### Basic Email Task

```python
from pydantic import EmailStr

async def send_email(to: str, subject: str, body: str):
    """Send email in background"""
    await asyncio.sleep(3)  # Simulate email sending
    print(f"Email sent to {to}: {subject}")

@app.post("/register")
async def register_user(
    email: EmailStr,
    username: str,
    background_tasks: BackgroundTasks
):
    # Save user to database
    users_db[email] = {"username": username}
    
    # Send welcome email in background
    background_tasks.add_task(
        send_email,
        email,
        "Welcome!",
        f"Hello {username}, welcome to our platform!"
    )
    
    return {"message": "User registered", "email": email}
```

### Multiple Emails Example

```python
@app.post("/order")
async def create_order(
    user_email: EmailStr,
    admin_email: EmailStr,
    order_details: dict,
    background_tasks: BackgroundTasks
):
    # Process order
    order_id = save_order(order_details)
    
    # Send email to user
    background_tasks.add_task(
        send_email,
        user_email,
        "Order Confirmation",
        f"Your order {order_id} is confirmed"
    )
    
    # Send email to admin
    background_tasks.add_task(
        send_email,
        admin_email,
        "New Order",
        f"New order {order_id} received"
    )
    
    return {"order_id": order_id}
```

### Real SMTP Example

```python
import smtplib
from email.mime.text import MIMEText

def send_smtp_email(to: str, subject: str, body: str):
    """Real SMTP email sending"""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "noreply@example.com"
    msg["To"] = to
    
    # Configure with your SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("your-email@gmail.com", "your-password")
        server.send_message(msg)

@app.post("/send-email")
async def send_email_endpoint(
    to: EmailStr,
    subject: str,
    body: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_smtp_email, to, subject, body)
    return {"message": "Email queued"}
```

---

## Best Practices

### 1. Keep Tasks Lightweight

❌ **Bad:**
```python
def heavy_task():
    # 10 minutes of processing
    process_million_records()
```

✅ **Good:**
```python
def lightweight_task():
    # Quick operation (< 1 minute)
    send_notification()
```

### 2. Handle Errors Gracefully

```python
def safe_task(data: str):
    try:
        risky_operation(data)
    except Exception as e:
        log_error(f"Task failed: {e}")
        # Don't let errors crash the app
```

### 3. Don't Return Values

Background tasks can't return values to the response (it's already sent!).

❌ **Bad:**
```python
def get_result():
    return "some result"  # This goes nowhere!

@app.get("/example")
async def example(background_tasks: BackgroundTasks):
    result = background_tasks.add_task(get_result)  # result is None!
    return {"result": result}
```

✅ **Good:**
```python
def save_result():
    result = compute_something()
    database.save(result)  # Save to database
    # Let client query it later

@app.get("/example")
async def example(background_tasks: BackgroundTasks):
    background_tasks.add_task(save_result)
    return {"message": "Processing started"}
```

### 4. Use Async for I/O Tasks

✅ **Good:**
```python
async def async_api_call():
    async with httpx.AsyncClient() as client:
        await client.post("https://api.example.com")
```

### 5. Log Task Execution

```python
def logged_task(name: str):
    logger.info(f"Task started: {name}")
    try:
        do_work()
        logger.info(f"Task completed: {name}")
    except Exception as e:
        logger.error(f"Task failed: {name} - {e}")
```

---

## Common Pitfalls

### Pitfall 1: Expecting Return Values

```python
# ❌ This doesn't work!
@app.get("/wrong")
async def wrong(background_tasks: BackgroundTasks):
    result = background_tasks.add_task(some_function)
    return {"value": result}  # result is always None!
```

### Pitfall 2: Long-Running Tasks

```python
# ❌ Bad: This blocks for too long
def very_long_task():
    time.sleep(600)  # 10 minutes!
    # What if server restarts?
```

### Pitfall 3: No Error Handling

```python
# ❌ Bad: Errors disappear silently
def unsafe_task():
    risky_operation()  # If this fails, you won't know!
```

### Pitfall 4: Database Connections

```python
# ❌ Bad: Using request-scoped DB session
@app.post("/example")
async def example(
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks
):
    def task():
        db.query(User).all()  # Session might be closed!
    
    background_tasks.add_task(task)
    return {}
```

✅ **Solution:** Create new session in task
```python
def task():
    db = SessionLocal()  # New session
    try:
        db.query(User).all()
    finally:
        db.close()
```

---

## When NOT to Use Background Tasks

### Use Celery/RQ Instead

For these scenarios, use a proper task queue (Celery, RQ, ARQ):

1. **Long-running tasks** (> 1 minute)
2. **Tasks requiring retry logic**
3. **Scheduled/periodic tasks**
4. **Tasks that must be guaranteed to complete**
5. **Tasks requiring monitoring/tracking**
6. **Distributed task processing**

### Example: When to Switch

```python
# ✅ OK for BackgroundTasks: Quick email
background_tasks.add_task(send_email, user.email, "Welcome!")

# ❌ Use Celery instead: Heavy processing
background_tasks.add_task(process_video, video_file)  # Could take hours!

# ❌ Use Celery instead: Needs retry
background_tasks.add_task(charge_credit_card, payment_info)  # Must succeed!

# ❌ Use Celery instead: Scheduled task
background_tasks.add_task(send_daily_report)  # Needs scheduling!
```

---

## Production Alternatives

### Celery

Best for: Complex workflows, retries, scheduling

```python
# Celery task
@celery.task(bind=True, max_retries=3)
def send_email_task(self, to, subject, body):
    try:
        send_email(to, subject, body)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

# In FastAPI
@app.post("/send")
async def send(email: str):
    send_email_task.delay(email, "Subject", "Body")
    return {"message": "Queued"}
```

### RQ (Redis Queue)

Best for: Simple task queue, Python-native

```python
from rq import Queue
from redis import Redis

redis_conn = Redis()
queue = Queue(connection=redis_conn)

@app.post("/process")
async def process(data: dict):
    job = queue.enqueue(process_data, data)
    return {"job_id": job.id}
```

### ARQ (Async RQ)

Best for: Async tasks with Redis

```python
# ARQ worker
async def send_email(ctx, to, subject, body):
    await send_email_async(to, subject, body)

# In FastAPI
@app.post("/send")
async def send(email: str):
    await arq_redis.enqueue_job('send_email', email, "Subject", "Body")
    return {"message": "Queued"}
```

---

## Summary

### Use BackgroundTasks When:
- Task is quick (< 1 minute)
- Fire-and-forget is acceptable
- Building MVP or simple app
- Sending notifications/emails
- Logging to external services

### Use Celery/RQ When:
- Task is long-running
- Need retry logic
- Need scheduling
- Task must be guaranteed
- Need monitoring/tracking
- Building production system

### Quick Decision Tree

```
Task takes < 1 minute?
├─ Yes → Failure is OK?
│  ├─ Yes → Use BackgroundTasks ✅
│  └─ No → Use Celery
└─ No → Use Celery
```

---

## Next Steps

1. Run the examples: `06_background_tasks_basic.py`
2. Try email example: `06_email_sending.py`
3. Experiment with async vs sync tasks
4. Learn Celery for production systems

## Resources

- [FastAPI Background Tasks Docs](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [RQ Documentation](https://python-rq.org/)
- [ARQ Documentation](https://arq-docs.helpmanual.io/)
