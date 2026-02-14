# Background Tasks Quick Reference

## Basic Syntax

### Import
```python
from fastapi import BackgroundTasks
```

### Add Single Task
```python
@app.post("/endpoint")
async def endpoint(background_tasks: BackgroundTasks):
    background_tasks.add_task(function_name, arg1, arg2, kwarg1=value)
    return {"message": "Task queued"}
```

### Add Multiple Tasks
```python
background_tasks.add_task(task_one)
background_tasks.add_task(task_two)
background_tasks.add_task(task_three)
# Execute in order after response sent
```

---

## Sync vs Async

### Synchronous Task
```python
def sync_task(data: str):
    time.sleep(5)  # Blocking
    process(data)
```

**Use for:**
- CPU-bound operations
- Blocking libraries
- Traditional SMTP

### Asynchronous Task
```python
async def async_task(data: str):
    await asyncio.sleep(5)  # Non-blocking
    await process(data)
```

**Use for:**
- I/O operations
- Network requests
- Modern async libraries

---

## Common Patterns

### Pattern 1: Send Email After Registration
```python
@app.post("/register")
async def register(email: str, background_tasks: BackgroundTasks):
    save_user(email)
    background_tasks.add_task(send_welcome_email, email)
    return {"message": "Registered"}
```

### Pattern 2: Multiple Notifications
```python
@app.post("/order")
async def order(user_email: str, admin_email: str, background_tasks: BackgroundTasks):
    order_id = create_order()
    background_tasks.add_task(notify_user, user_email, order_id)
    background_tasks.add_task(notify_admin, admin_email, order_id)
    return {"order_id": order_id}
```

### Pattern 3: Cleanup Resources
```python
@app.delete("/file/{file_id}")
async def delete_file(file_id: int, background_tasks: BackgroundTasks):
    mark_deleted(file_id)
    background_tasks.add_task(remove_from_storage, file_id)
    return {"message": "File deleted"}
```

### Pattern 4: Log to External Service
```python
@app.post("/action")
async def action(data: dict, background_tasks: BackgroundTasks):
    result = perform_action(data)
    background_tasks.add_task(log_to_analytics, data, result)
    return result
```

---

## Email Sending

### Simple Email
```python
async def send_email(to: str, subject: str, body: str):
    await asyncio.sleep(2)  # Simulate
    print(f"Email sent to {to}")

@app.post("/send")
async def send(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email, "Subject", "Body")
    return {"message": "Email queued"}
```

### With Template
```python
def get_welcome_email(username: str) -> str:
    return f"Welcome {username}!"

@app.post("/register")
async def register(username: str, email: str, background_tasks: BackgroundTasks):
    save_user(username, email)
    body = get_welcome_email(username)
    background_tasks.add_task(send_email, email, "Welcome", body)
    return {"message": "Registered"}
```

### Bulk Email
```python
@app.post("/bulk-email")
async def bulk(recipients: List[str], background_tasks: BackgroundTasks):
    for recipient in recipients:
        background_tasks.add_task(send_email, recipient, "News", "Body")
    return {"count": len(recipients)}
```

---

## Error Handling

### With Try-Except
```python
def safe_task(data: str):
    try:
        risky_operation(data)
    except Exception as e:
        log_error(f"Task failed: {e}")
```

### With Logging
```python
import logging

def logged_task(name: str):
    logging.info(f"Task started: {name}")
    try:
        do_work()
        logging.info(f"Task completed: {name}")
    except Exception as e:
        logging.error(f"Task failed: {name} - {e}")
```

---

## Database Access

### ❌ WRONG: Using Request-Scoped Session
```python
@app.post("/wrong")
async def wrong(db: Session = Depends(get_db), background_tasks: BackgroundTasks):
    def task():
        db.query(User).all()  # Session closed!
    background_tasks.add_task(task)
```

### ✅ CORRECT: Create New Session
```python
@app.post("/correct")
async def correct(background_tasks: BackgroundTasks):
    def task():
        db = SessionLocal()  # New session
        try:
            db.query(User).all()
        finally:
            db.close()
    background_tasks.add_task(task)
```

---

## Best Practices

### ✅ DO
- Keep tasks under 1 minute
- Use async for I/O operations
- Handle errors gracefully
- Log task execution
- Create new DB sessions in tasks
- Use for fire-and-forget operations

### ❌ DON'T
- Expect return values
- Use for long-running tasks (> 1 minute)
- Use for critical operations requiring retries
- Use request-scoped dependencies
- Use for scheduled tasks
- Assume tasks always succeed

---

## When to Use Alternatives

| Use BackgroundTasks | Use Celery/RQ |
|---------------------|---------------|
| Task < 1 minute | Task > 1 minute |
| Fire-and-forget OK | Must complete |
| Simple operations | Need retries |
| MVP/prototyping | Production system |
| Sending emails | Video processing |
| Logging events | Payment processing |
| Cache updates | Report generation |

---

## Complete Example

```python
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, EmailStr
import asyncio
from datetime import datetime

app = FastAPI()

class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    full_name: str

# Background task functions
async def send_welcome_email(email: str, username: str):
    await asyncio.sleep(2)
    print(f"📧 Welcome email sent to {email}")

def log_registration(username: str):
    timestamp = datetime.now().isoformat()
    with open("registration.log", "a") as f:
        f.write(f"{timestamp} - User registered: {username}\n")

def update_analytics(event: str, data: dict):
    # Simulate analytics API call
    print(f"📊 Analytics updated: {event} - {data}")

# Endpoint with multiple background tasks
@app.post("/register")
async def register(
    user: UserRegistration,
    background_tasks: BackgroundTasks
):
    # Save user (immediate)
    users_db[user.email] = user.dict()
    
    # Queue background tasks
    background_tasks.add_task(
        send_welcome_email, 
        user.email, 
        user.username
    )
    background_tasks.add_task(
        log_registration, 
        user.username
    )
    background_tasks.add_task(
        update_analytics,
        "user_registered",
        {"username": user.username}
    )
    
    # Response sent immediately!
    return {
        "message": "Registration successful",
        "username": user.username,
        "note": "Welcome email will arrive shortly"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Testing Background Tasks

### Test That Task Was Added
```python
def test_background_task():
    # Create a mock BackgroundTasks
    from fastapi import BackgroundTasks
    
    tasks = BackgroundTasks()
    
    # Your endpoint should add tasks
    response = client.post("/endpoint")
    
    # Verify response
    assert response.status_code == 200
```

### Run Tasks Manually in Tests
```python
def test_task_execution():
    # Call the background task directly
    result = send_email("test@example.com", "Subject", "Body")
    
    # Verify the task worked
    assert email_was_sent(result)
```

---

## Quick Decision Tree

```
Do you need the result in the response?
├─ Yes → Don't use BackgroundTasks (compute before return)
└─ No → Continue...

Does the task take > 1 minute?
├─ Yes → Use Celery/RQ
└─ No → Continue...

Must the task always succeed?
├─ Yes → Use Celery/RQ (with retries)
└─ No → Continue...

Is it a scheduled/periodic task?
├─ Yes → Use Celery Beat / APScheduler
└─ No → Use BackgroundTasks ✅
```

---

## Real-World Examples

### 1. User Registration Flow
```python
@app.post("/register")
async def register(user: User, background_tasks: BackgroundTasks):
    save_user(user)
    background_tasks.add_task(send_welcome_email, user.email)
    background_tasks.add_task(setup_default_preferences, user.id)
    background_tasks.add_task(notify_admin_new_user, user.email)
    return {"message": "Welcome!"}
```

### 2. File Upload Processing
```python
@app.post("/upload")
async def upload(file: UploadFile, background_tasks: BackgroundTasks):
    file_path = save_file(file)
    background_tasks.add_task(generate_thumbnail, file_path)
    background_tasks.add_task(scan_for_viruses, file_path)
    background_tasks.add_task(update_file_index, file_path)
    return {"file_id": file_path}
```

### 3. Order Confirmation
```python
@app.post("/order")
async def create_order(order: Order, background_tasks: BackgroundTasks):
    order_id = save_order(order)
    background_tasks.add_task(send_order_confirmation, order.email)
    background_tasks.add_task(notify_warehouse, order_id)
    background_tasks.add_task(update_inventory, order.items)
    return {"order_id": order_id}
```

---

## Common Gotchas

### Gotcha 1: Return Values
```python
# ❌ Won't work
result = background_tasks.add_task(compute)  # result is None!
```

### Gotcha 2: Task Fails Silently
```python
# ❌ Error disappears
def task():
    raise Exception("Oops!")  # You won't see this!

# ✅ Handle errors
def task():
    try:
        risky_operation()
    except Exception as e:
        logger.error(f"Task failed: {e}")
```

### Gotcha 3: Shared State
```python
# ❌ Race condition possible
counter = 0

def increment():
    global counter
    counter += 1  # Not thread-safe!

# ✅ Use proper synchronization or database
def increment():
    with lock:
        counter += 1
```

---

## Resources

- **Docs:** https://fastapi.tiangolo.com/tutorial/background-tasks/
- **Celery:** https://docs.celeryproject.org/
- **RQ:** https://python-rq.org/
- **ARQ:** https://arq-docs.helpmanual.io/
