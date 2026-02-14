# 🔄 Module 06: Background Tasks

Learn how to execute tasks in the background after returning responses to clients using FastAPI's BackgroundTasks.

## 📚 What You'll Learn

- ✅ BackgroundTasks basics
- ✅ Async vs sync background tasks
- ✅ Email sending with background tasks
- ✅ Multiple background tasks
- ✅ Error handling in background tasks
- ✅ When to use BackgroundTasks vs Celery
- ✅ Best practices and common pitfalls

## 📁 Files in This Module

| File | Description |
|------|-------------|
| `06_background_tasks_basic.py` | Basic BackgroundTasks examples with sync/async |
| `06_email_sending.py` | Realistic email sending scenarios |
| `06_BACKGROUND_TASKS_TUTORIAL.md` | Complete tutorial with explanations |
| `BACKGROUND_TASKS_CHEATSHEET.md` | Quick reference guide |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install fastapi uvicorn pydantic[email]
```

### 2. Run Basic Example

```bash
# Terminal 1: Start the server
python 06_background_tasks/06_background_tasks_basic.py

# Terminal 2: Test the endpoints
curl -X POST "http://localhost:8000/simple/notification" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "message": "Hello!"}'
```

### 3. Run Email Example

```bash
# Terminal 1: Start the email server
python 06_background_tasks/06_email_sending.py

# Terminal 2: Register a user
curl -X POST "http://localhost:8001/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "full_name": "John Doe"
  }'
```

## 📖 Examples

### Example 1: Simple Background Task

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

def send_email(email: str, message: str):
    print(f"Sending email to {email}: {message}")

@app.post("/notify")
async def notify(email: str, background_tasks: BackgroundTasks):
    # Response sent immediately!
    background_tasks.add_task(send_email, email, "Hello!")
    return {"message": "Notification queued"}
```

### Example 2: Multiple Background Tasks

```python
@app.post("/order")
async def create_order(email: str, background_tasks: BackgroundTasks):
    # All three tasks run after response is sent
    background_tasks.add_task(process_payment)
    background_tasks.add_task(send_confirmation_email, email)
    background_tasks.add_task(update_inventory)
    
    return {"message": "Order created"}
```

### Example 3: Async Background Task

```python
async def async_send_email(email: str):
    await asyncio.sleep(2)  # Non-blocking
    print(f"Email sent to {email}")

@app.post("/register")
async def register(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(async_send_email, email)
    return {"message": "Registered"}
```

## 🎯 Key Concepts

### What are Background Tasks?

Background tasks are functions that run **after** the response is sent to the client. The client doesn't wait for them to complete.

**Perfect for:**
- Sending emails 📧
- Logging events 📝
- Generating reports 📊
- Cleaning up resources 🧹
- Updating cache 💾

### Sync vs Async Tasks

| Type | Use For | Example |
|------|---------|---------|
| **Sync** (`def`) | Blocking operations | Traditional SMTP, CPU-bound tasks |
| **Async** (`async def`) | I/O operations | HTTP requests, async database queries |

```python
# Sync task
def sync_task():
    time.sleep(5)  # Blocking

# Async task (more efficient!)
async def async_task():
    await asyncio.sleep(5)  # Non-blocking
```

### When to Use BackgroundTasks

✅ **Use BackgroundTasks:**
- Task takes < 1 minute
- Fire-and-forget is OK
- Simple operations
- MVP/prototyping

❌ **Use Celery/RQ Instead:**
- Task takes > 1 minute
- Need retry logic
- Must guarantee completion
- Need monitoring/tracking

## 🧪 Interactive Testing

### Test with cURL

```bash
# Simple notification
curl -X POST "http://localhost:8000/simple/notification" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "message": "Test message"}'

# Create order (multiple tasks)
curl -X POST "http://localhost:8000/order" \
  -H "Content-Type: application/json" \
  -d '{
    "item": "Laptop",
    "quantity": 1,
    "email": "customer@example.com"
  }'

# Check logs
curl "http://localhost:8000/logs"
```

### Test with Python requests

```python
import requests

# Send notification
response = requests.post(
    "http://localhost:8000/simple/notification",
    json={
        "email": "user@example.com",
        "message": "Hello from Python!"
    }
)
print(response.json())

# Create order
response = requests.post(
    "http://localhost:8000/order",
    json={
        "item": "Book",
        "quantity": 3,
        "email": "reader@example.com"
    }
)
print(response.json())
```

### Test with FastAPI Docs

1. Start the server
2. Open http://localhost:8000/docs
3. Try the endpoints interactively
4. Watch the console for task execution logs

## 📊 Real-World Scenarios

### Scenario 1: User Registration

```python
@app.post("/register")
async def register(user: User, background_tasks: BackgroundTasks):
    # Save user first (immediate)
    save_user(user)
    
    # Background tasks (after response)
    background_tasks.add_task(send_welcome_email, user.email)
    background_tasks.add_task(setup_user_preferences, user.id)
    background_tasks.add_task(notify_admin, user.email)
    
    return {"message": "Welcome!"}
```

### Scenario 2: File Upload

```python
@app.post("/upload")
async def upload(file: UploadFile, background_tasks: BackgroundTasks):
    file_path = save_file(file)
    
    # Process file in background
    background_tasks.add_task(generate_thumbnail, file_path)
    background_tasks.add_task(extract_metadata, file_path)
    background_tasks.add_task(scan_virus, file_path)
    
    return {"file_id": file_path}
```

### Scenario 3: Order Processing

```python
@app.post("/checkout")
async def checkout(order: Order, background_tasks: BackgroundTasks):
    order_id = create_order(order)
    
    background_tasks.add_task(charge_payment, order.payment_info)
    background_tasks.add_task(send_confirmation, order.email)
    background_tasks.add_task(notify_warehouse, order_id)
    background_tasks.add_task(update_analytics, order_id)
    
    return {"order_id": order_id}
```

## 🎓 Learning Path

1. **Start Here:** Read the [Tutorial](06_BACKGROUND_TASKS_TUTORIAL.md)
2. **Run Examples:** Execute `06_background_tasks_basic.py`
3. **Email Example:** Try `06_email_sending.py`
4. **Quick Reference:** Use [Cheatsheet](BACKGROUND_TASKS_CHEATSHEET.md)
5. **Practice:** Build your own examples

## 💡 Best Practices

### DO ✅

```python
# Keep tasks short
def quick_task():
    send_notification()  # < 1 minute

# Handle errors
def safe_task():
    try:
        risky_operation()
    except Exception as e:
        log_error(e)

# Use async for I/O
async def efficient_task():
    await send_http_request()
```

### DON'T ❌

```python
# Don't expect return values
result = background_tasks.add_task(compute)  # result is None!

# Don't use for long tasks
def long_task():
    time.sleep(600)  # Use Celery instead!

# Don't reuse request dependencies
def task(db: Session):  # Session might be closed!
    db.query(User).all()
```

## 🔍 Common Patterns

### Pattern 1: Email After Action
```python
background_tasks.add_task(send_email, user.email, "Action completed")
```

### Pattern 2: Cleanup Resources
```python
background_tasks.add_task(delete_temp_files, file_path)
```

### Pattern 3: Log Event
```python
background_tasks.add_task(log_to_analytics, event_data)
```

### Pattern 4: Update Cache
```python
background_tasks.add_task(invalidate_cache, cache_key)
```

## 🐛 Debugging Tips

### View Task Logs

```python
import logging

logging.basicConfig(level=logging.INFO)

def logged_task(name: str):
    logging.info(f"Task started: {name}")
    try:
        do_work()
        logging.info(f"Task completed: {name}")
    except Exception as e:
        logging.error(f"Task failed: {name} - {e}")
```

### Track Task Execution

```python
task_log = []

def tracked_task(name: str):
    start = time.time()
    try:
        do_work()
        duration = time.time() - start
        task_log.append({"name": name, "duration": duration, "status": "success"})
    except Exception as e:
        task_log.append({"name": name, "error": str(e), "status": "failed"})
```

## 📚 Additional Resources

### Official Documentation
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Starlette Background Tasks](https://www.starlette.io/background/)

### Task Queues for Production
- [Celery](https://docs.celeryproject.org/)
- [RQ (Redis Queue)](https://python-rq.org/)
- [ARQ (Async RQ)](https://arq-docs.helpmanual.io/)

### Related Topics
- Module 03: Dependency Injection
- Module 05: Authentication
- Module 04: Database Integration

## 🎯 Exercises

### Exercise 1: Basic Background Task
Create an endpoint that logs user actions in the background.

### Exercise 2: Email Service
Build a registration system that sends welcome emails.

### Exercise 3: File Processing
Create a file upload endpoint that processes files in the background.

### Exercise 4: Multiple Tasks
Build an order system with multiple background tasks:
- Send confirmation email
- Update inventory
- Notify warehouse
- Log analytics

## 🤝 Need Help?

- Check the [Tutorial](06_BACKGROUND_TASKS_TUTORIAL.md) for detailed explanations
- Use the [Cheatsheet](BACKGROUND_TASKS_CHEATSHEET.md) for quick reference
- Review the example files for working code

## 🚀 Next Steps

After mastering background tasks, explore:
- **Celery:** For production-grade task queues
- **WebSockets:** For real-time updates
- **Async/Await:** For advanced async patterns
- **Testing:** Testing background tasks

---

**Happy coding! 🎉**
