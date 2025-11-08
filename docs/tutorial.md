# Tutorial: Building a Task Management API

In this tutorial, we'll build a complete task management API that demonstrates all the key features of `pyramid-capstone`. You'll learn about parameter handling, validation, error handling, and more.

## What We'll Build

A task management API with the following features:

- ✅ Create, read, update, and delete tasks
- 🏷️ Task categories and priorities  
- 👤 User assignment
- 🔍 Filtering and pagination
- ✨ Automatic validation and documentation

## Step 1: Project Setup

Create a new directory and set up the basic structure:

```bash
mkdir task-api
cd task-api
```

Create `pyproject.toml`:

```toml
[tool.poetry]
name = "task-api"
version = "0.1.0"
description = "Task management API example"
authors = ["Your Name <your.email@example.com>"]

[tool.poetry.dependencies]
python = "^3.8"
pyramid-capstone = "^0.1.0"
waitress = "^2.1.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

Install dependencies:

```bash
poetry install
```

## Step 2: Define Data Models

Create `models.py` to define our data structures:

```python
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import uuid4

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    URGENT = "urgent"

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

@dataclass
class User:
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    email: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass  
class Category:
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: Optional[str] = None
    color: str = "#007bff"

@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM
    assignee_id: Optional[str] = None
    category_id: Optional[str] = None
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

# Response models for API
@dataclass
class TaskResponse:
    """Task with populated assignee and category information."""
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: Priority
    assignee: Optional[User]
    category: Optional[Category]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

@dataclass
class TaskListResponse:
    """Paginated list of tasks."""
    tasks: List[TaskResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
```

## Step 3: Create Data Storage

Create `storage.py` for in-memory data storage:

```python
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .models import Task, User, Category, TaskStatus, Priority

class TaskStorage:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.users: Dict[str, User] = {}
        self.categories: Dict[str, Category] = {}
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Initialize with some sample data."""
        # Create sample users
        user1 = User(name="Alice Johnson", email="alice@example.com")
        user2 = User(name="Bob Smith", email="bob@example.com")
        self.users[user1.id] = user1
        self.users[user2.id] = user2
        
        # Create sample categories
        cat1 = Category(name="Work", description="Work-related tasks", color="#dc3545")
        cat2 = Category(name="Personal", description="Personal tasks", color="#28a745")
        self.categories[cat1.id] = cat1
        self.categories[cat2.id] = cat2
        
        # Create sample tasks
        task1 = Task(
            title="Complete project proposal",
            description="Write and review the Q4 project proposal",
            priority=Priority.HIGH,
            assignee_id=user1.id,
            category_id=cat1.id,
            due_date=datetime.now() + timedelta(days=3)
        )
        task2 = Task(
            title="Buy groceries",
            description="Milk, bread, eggs, vegetables",
            priority=Priority.MEDIUM,
            assignee_id=user2.id,
            category_id=cat2.id,
            status=TaskStatus.TODO
        )
        self.tasks[task1.id] = task1
        self.tasks[task2.id] = task2
    
    # Task operations
    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)
    
    def create_task(self, task: Task) -> Task:
        task.created_at = datetime.now()
        task.updated_at = datetime.now()
        self.tasks[task.id] = task
        return task
    
    def update_task(self, task_id: str, updates: dict) -> Optional[Task]:
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        task.updated_at = datetime.now()
        return task
    
    def delete_task(self, task_id: str) -> bool:
        return self.tasks.pop(task_id, None) is not None
    
    def list_tasks(self, status: Optional[TaskStatus] = None,
                   priority: Optional[Priority] = None,
                   assignee_id: Optional[str] = None,
                   category_id: Optional[str] = None,
                   page: int = 1, per_page: int = 10) -> tuple:
        """List tasks with filtering and pagination."""
        tasks = list(self.tasks.values())
        
        # Apply filters
        if status:
            tasks = [t for t in tasks if t.status == status]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        if assignee_id:
            tasks = [t for t in tasks if t.assignee_id == assignee_id]
        if category_id:
            tasks = [t for t in tasks if t.category_id == category_id]
        
        # Sort by created_at descending
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        # Pagination
        total = len(tasks)
        start = (page - 1) * per_page
        end = start + per_page
        page_tasks = tasks[start:end]
        
        return page_tasks, total
    
    # User operations
    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)
    
    def list_users(self) -> List[User]:
        return list(self.users.values())
    
    # Category operations
    def get_category(self, category_id: str) -> Optional[Category]:
        return self.categories.get(category_id)
    
    def list_categories(self) -> List[Category]:
        return list(self.categories.values())

# Global storage instance
storage = TaskStorage()
```

## Step 4: Build the API Endpoints

Create `views.py` with our API endpoints:

```python
from typing import Optional, List
from pyramid.request import Request
from pyramid_capstone import api
from .models import (
    Task, TaskResponse, TaskListResponse, TaskStatus, Priority,
    User, Category
)
from .storage import storage

# Helper function to build task response with populated relationships
def build_task_response(task: Task) -> TaskResponse:
    """Convert Task to TaskResponse with populated relationships."""
    assignee = storage.get_user(task.assignee_id) if task.assignee_id else None
    category = storage.get_category(task.category_id) if task.category_id else None
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        assignee=assignee,
        category=category,
        due_date=task.due_date,
        created_at=task.created_at,
        updated_at=task.updated_at
    )

# Task endpoints
@api.get('/tasks')
def list_tasks(request: Request,
               status: Optional[str] = None,
               priority: Optional[str] = None,
               assignee_id: Optional[str] = None,
               category_id: Optional[str] = None,
               page: int = 1,
               per_page: int = 10) -> TaskListResponse:
    """List tasks with optional filtering and pagination."""
    
    # Convert string enums to enum objects
    status_enum = TaskStatus(status) if status else None
    priority_enum = Priority(priority) if priority else None
    
    # Validate pagination parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 10
    
    tasks, total = storage.list_tasks(
        status=status_enum,
        priority=priority_enum,
        assignee_id=assignee_id,
        category_id=category_id,
        page=page,
        per_page=per_page
    )
    
    # Build response objects
    task_responses = [build_task_response(task) for task in tasks]
    
    return TaskListResponse(
        tasks=task_responses,
        total=total,
        page=page,
        per_page=per_page,
        has_next=(page * per_page) < total,
        has_prev=page > 1
    )

@api.get('/tasks/{task_id}')
def get_task(request: Request, task_id: str) -> TaskResponse:
    """Get a specific task by ID."""
    task = storage.get_task(task_id)
    if not task:
        request.response.status = 404
        return {"error": "Task not found"}
    
    return build_task_response(task)

@api.post('/tasks')
def create_task(request: Request,
                title: str,
                description: Optional[str] = None,
                priority: str = "medium",
                assignee_id: Optional[str] = None,
                category_id: Optional[str] = None) -> TaskResponse:
    """Create a new task."""
    
    # Validate priority
    try:
        priority_enum = Priority(priority)
    except ValueError:
        request.response.status = 400
        return {"error": f"Invalid priority. Must be one of: {[p.value for p in Priority]}"}
    
    # Validate assignee exists
    if assignee_id and not storage.get_user(assignee_id):
        request.response.status = 400
        return {"error": "Assignee not found"}
    
    # Validate category exists
    if category_id and not storage.get_category(category_id):
        request.response.status = 400
        return {"error": "Category not found"}
    
    # Create task
    task = Task(
        title=title,
        description=description,
        priority=priority_enum,
        assignee_id=assignee_id,
        category_id=category_id
    )
    
    created_task = storage.create_task(task)
    request.response.status = 201
    return build_task_response(created_task)

@api.put('/tasks/{task_id}')
def update_task(request: Request,
                task_id: str,
                title: Optional[str] = None,
                description: Optional[str] = None,
                status: Optional[str] = None,
                priority: Optional[str] = None,
                assignee_id: Optional[str] = None,
                category_id: Optional[str] = None) -> TaskResponse:
    """Update an existing task."""
    
    task = storage.get_task(task_id)
    if not task:
        request.response.status = 404
        return {"error": "Task not found"}
    
    updates = {}
    
    # Build updates dict with validation
    if title is not None:
        updates['title'] = title
    if description is not None:
        updates['description'] = description
    if status is not None:
        try:
            updates['status'] = TaskStatus(status)
        except ValueError:
            request.response.status = 400
            return {"error": f"Invalid status. Must be one of: {[s.value for s in TaskStatus]}"}
    if priority is not None:
        try:
            updates['priority'] = Priority(priority)
        except ValueError:
            request.response.status = 400
            return {"error": f"Invalid priority. Must be one of: {[p.value for p in Priority]}"}
    if assignee_id is not None:
        if assignee_id and not storage.get_user(assignee_id):
            request.response.status = 400
            return {"error": "Assignee not found"}
        updates['assignee_id'] = assignee_id
    if category_id is not None:
        if category_id and not storage.get_category(category_id):
            request.response.status = 400
            return {"error": "Category not found"}
        updates['category_id'] = category_id
    
    updated_task = storage.update_task(task_id, updates)
    return build_task_response(updated_task)

@api.delete('/tasks/{task_id}')
def delete_task(request: Request, task_id: str) -> dict:
    """Delete a task."""
    if not storage.delete_task(task_id):
        request.response.status = 404
        return {"error": "Task not found"}
    
    return {"message": "Task deleted successfully"}

# User endpoints
@api.get('/users')
def list_users(request: Request) -> List[User]:
    """List all users."""
    return storage.list_users()

@api.get('/users/{user_id}')
def get_user(request: Request, user_id: str) -> User:
    """Get a specific user by ID."""
    user = storage.get_user(user_id)
    if not user:
        request.response.status = 404
        return {"error": "User not found"}
    return user

# Category endpoints
@api.get('/categories')
def list_categories(request: Request) -> List[Category]:
    """List all categories."""
    return storage.list_categories()

@api.get('/categories/{category_id}')
def get_category(request: Request, category_id: str) -> Category:
    """Get a specific category by ID."""
    category = storage.get_category(category_id)
    if not category:
        request.response.status = 404
        return {"error": "Category not found"}
    return category

# Health check
@api.get('/health')
def health_check(request: Request) -> dict:
    """API health check."""
    return {
        "status": "healthy",
        "tasks_count": len(storage.tasks),
        "users_count": len(storage.users),
        "categories_count": len(storage.categories)
    }
```

## Step 5: Create the Application

Create `app.py`:

```python
from pyramid.config import Configurator

def main(global_config, **settings):
    """Create and configure the Pyramid application."""
    config = Configurator(settings=settings)
    
    # Include pyramid-capstone
    config.include('pyramid_capstone')
    
    # Scan for decorated views
    config.scan()
    
    return config.make_wsgi_app()

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    app = main({})
    server = make_server('0.0.0.0', 6543, app)
    print("Task API running on http://localhost:6543")
    print("Try: curl http://localhost:6543/health")
    server.serve_forever()
```

## Step 6: Test Your API

Run the application:

```bash
python app.py
```

Now test the endpoints:

### Health Check
```bash
curl http://localhost:6543/health
```

### List Tasks
```bash
# All tasks
curl http://localhost:6543/tasks

# Filter by status
curl "http://localhost:6543/tasks?status=todo"

# Filter by priority
curl "http://localhost:6543/tasks?priority=high"

# Pagination
curl "http://localhost:6543/tasks?page=1&per_page=5"
```

### Create a Task
```bash
curl -X POST http://localhost:6543/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn pyramid-capstone",
    "description": "Complete the tutorial and build an API",
    "priority": "high"
  }'
```

### Update a Task
```bash
# First get a task ID from the list, then:
curl -X PUT http://localhost:6543/tasks/{task_id} \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "priority": "urgent"
  }'
```

### Get Users and Categories
```bash
curl http://localhost:6543/users
curl http://localhost:6543/categories
```

## What You've Learned

Congratulations! You've built a complete API that demonstrates:

### 🔍 **Parameter Handling**
- Path parameters (`task_id`)
- Query parameters with defaults (`page=1`, `per_page=10`)
- Optional parameters (`description`, `assignee_id`)
- JSON body parameters with validation

### ✅ **Automatic Validation**
- Type conversion (strings to integers for pagination)
- Required vs optional parameters
- Enum validation for status and priority
- Custom validation logic with proper error responses

### 📊 **Complex Data Structures**
- Dataclasses for clean data models
- Nested objects (tasks with assignee and category info)
- Lists and pagination responses
- Enum types for controlled values

### 🛠️ **Real-World Patterns**
- CRUD operations (Create, Read, Update, Delete)
- Filtering and pagination
- Relationship handling
- Error handling with appropriate HTTP status codes

## Next Steps

Now that you understand the basics, you might want to:

- **[Add Security](security.md)** - Protect your endpoints with authentication
- **[Explore Examples](examples.md)** - See more advanced use cases

## Advanced Features Preview

Here are some advanced features you can explore:

### Custom Validation
```python
@api.post('/tasks')
def create_task(request: Request, title: str, due_date: str) -> TaskResponse:
    # Custom date validation
    try:
        due_date_obj = datetime.fromisoformat(due_date)
        if due_date_obj < datetime.now():
            request.response.status = 400
            return {"error": "Due date must be in the future"}
    except ValueError:
        request.response.status = 400
        return {"error": "Invalid date format. Use ISO format: YYYY-MM-DD"}
```

### Nested Objects
```python
from dataclasses import dataclass

@dataclass
class TaskWithComments:
    task: Task
    comments: List[str]

@api.get('/tasks/{task_id}/full')
def get_task_with_comments(request: Request, task_id: str) -> TaskWithComments:
    # Return complex nested structures
    pass
```

### File Uploads
```python
@api.post('/tasks/{task_id}/attachments')
def upload_attachment(request: Request, task_id: str) -> dict:
    # Handle file uploads through request.POST
    upload = request.POST.get('file')
    if upload:
        # Process the uploaded file
        pass
```

Ready to explore more patterns? Check out our [Examples](examples.md) guide!
