"""
Simple To-Do API built with FastAPI
Demonstrates: routes, path/query parameters, Pydantic models, CRUD operations
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="To-Do API",
    description="A simple To-Do API built with FastAPI",
    version="1.0.0"
)

# Pydantic models for request/response validation
class Task(BaseModel):
    """Task model with automatic validation"""
    title: str = Field(..., min_length=1, max_length=100, description="Task title")
    description: Optional[str] = Field(None, max_length=500, description="Task description")
    completed: bool = Field(False, description="Task completion status")

class TaskResponse(Task):
    """Response model includes the task ID and timestamp"""
    id: int
    created_at: datetime

class TaskUpdate(BaseModel):
    """Model for updating tasks - all fields optional"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    completed: Optional[bool] = None

# In-memory database (for learning purposes)
tasks_db = {}
task_counter = 0

# Route: Root endpoint
@app.get("/", tags=["Root"])
def read_root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to the To-Do API!",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Route: Create a new task
@app.post("/tasks", response_model=TaskResponse, status_code=201, tags=["Tasks"])
def create_task(task: Task):
    """
    Create a new task
    
    - **title**: Task title (required)
    - **description**: Task description (optional)
    - **completed**: Completion status (default: False)
    """
    global task_counter
    task_counter += 1
    
    new_task = {
        "id": task_counter,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": datetime.now()
    }
    
    tasks_db[task_counter] = new_task
    return new_task

# Route: List all tasks (with optional filtering)
@app.get("/tasks", response_model=List[TaskResponse], tags=["Tasks"])
def list_tasks(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of tasks to return")
):
    """
    List all tasks
    
    - **completed**: Filter by completion status (optional query parameter)
    - **limit**: Maximum number of tasks to return (default: 10)
    """
    tasks = list(tasks_db.values())
    
    # Filter by completion status if specified
    if completed is not None:
        tasks = [task for task in tasks if task["completed"] == completed]
    
    # Apply limit
    tasks = tasks[:limit]
    
    return tasks

# Route: Get a single task by ID (path parameter)
@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def get_task(task_id: int):
    """
    Get a specific task by ID
    
    - **task_id**: Task ID (path parameter)
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    
    return tasks_db[task_id]

# Route: Update a task
@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def update_task(task_id: int, task_update: TaskUpdate):
    """
    Update an existing task
    
    - **task_id**: Task ID (path parameter)
    - Only provided fields will be updated
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    
    # Update only the fields that were provided
    task = tasks_db[task_id]
    update_data = task_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        task[field] = value
    
    return task

# Route: Delete a task
@app.delete("/tasks/{task_id}", status_code=204, tags=["Tasks"])
def delete_task(task_id: int):
    """
    Delete a task
    
    - **task_id**: Task ID (path parameter)
    """
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found")
    
    del tasks_db[task_id]
    return None

# Route: Delete all tasks
@app.delete("/tasks", status_code=204, tags=["Tasks"])
def delete_all_tasks():
    """Delete all tasks"""
    global tasks_db, task_counter
    tasks_db = {}
    task_counter = 0
    return None

# Route: Health check
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "total_tasks": len(tasks_db)
    }
