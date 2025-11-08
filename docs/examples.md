# Examples

This page showcases real-world examples and patterns using `pyramid-capstone`.

## Complete Blog API Example

The repository includes a comprehensive [Blog API example](https://github.com/tomas_correa/pyramid-capstone/tree/main/examples/blog_api) that demonstrates:

- **CRUD operations** for users, posts, comments, and categories
- **Complex parameter handling** with filtering and pagination
- **Nested relationships** between entities
- **Error handling** with proper HTTP status codes
- **OpenAPI documentation** with Swagger UI

### Running the Blog Example

```bash
# Clone the repository
git clone https://github.com/tomas_correa/pyramid-capstone.git
cd pyramid-capstone

# Install dependencies
poetry install --with dev

# Run the blog API
cd examples/blog_api
pserve development.ini

# Visit http://localhost:6543 for API documentation
# Visit http://localhost:6543/swagger-ui/ for interactive docs
```

## Common Patterns

### 1. Simple CRUD Operations

```python
from pyramid_capstone import api
from typing import List, Optional

# In-memory storage for demo
books = {}
next_id = 1

@api.get('/books')
def list_books(request, 
               author: Optional[str] = None,
               genre: Optional[str] = None,
               page: int = 1,
               per_page: int = 10) -> dict:
    """List books with optional filtering and pagination."""
    filtered_books = list(books.values())
    
    # Apply filters
    if author:
        filtered_books = [b for b in filtered_books if author.lower() in b['author'].lower()]
    if genre:
        filtered_books = [b for b in filtered_books if b['genre'].lower() == genre.lower()]
    
    # Pagination
    total = len(filtered_books)
    start = (page - 1) * per_page
    end = start + per_page
    page_books = filtered_books[start:end]
    
    return {
        "books": page_books,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "has_next": end < total,
            "has_prev": page > 1
        }
    }

@api.get('/books/{book_id}')
def get_book(request, book_id: int) -> dict:
    """Get a specific book by ID."""
    book = books.get(book_id)
    if not book:
        request.response.status = 404
        return {"error": "Book not found"}
    return book

@api.post('/books')
def create_book(request, 
                title: str, 
                author: str, 
                genre: str,
                isbn: Optional[str] = None,
                pages: Optional[int] = None) -> dict:
    """Create a new book."""
    global next_id
    
    # Validation
    if len(title.strip()) < 1:
        request.response.status = 400
        return {"error": "Title is required"}
    
    if len(author.strip()) < 1:
        request.response.status = 400
        return {"error": "Author is required"}
    
    book = {
        "id": next_id,
        "title": title.strip(),
        "author": author.strip(),
        "genre": genre.strip(),
        "isbn": isbn,
        "pages": pages,
        "created_at": datetime.now().isoformat()
    }
    
    books[next_id] = book
    next_id += 1
    
    request.response.status = 201
    return book

@api.put('/books/{book_id}')
def update_book(request, 
                book_id: int,
                title: Optional[str] = None,
                author: Optional[str] = None,
                genre: Optional[str] = None,
                isbn: Optional[str] = None,
                pages: Optional[int] = None) -> dict:
    """Update an existing book."""
    book = books.get(book_id)
    if not book:
        request.response.status = 404
        return {"error": "Book not found"}
    
    # Update provided fields
    if title is not None:
        book["title"] = title.strip()
    if author is not None:
        book["author"] = author.strip()
    if genre is not None:
        book["genre"] = genre.strip()
    if isbn is not None:
        book["isbn"] = isbn
    if pages is not None:
        book["pages"] = pages
    
    book["updated_at"] = datetime.now().isoformat()
    return book

@api.delete('/books/{book_id}')
def delete_book(request, book_id: int) -> dict:
    """Delete a book."""
    if book_id not in books:
        request.response.status = 404
        return {"error": "Book not found"}
    
    del books[book_id]
    return {"message": "Book deleted successfully"}
```

### 2. File Upload Handling

```python
import os
import uuid
from pyramid_capstone import api

UPLOAD_DIR = "/tmp/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@api.post('/upload')
def upload_file(request, description: Optional[str] = None) -> dict:
    """Upload a file with optional description."""
    
    # Get uploaded file from request
    if 'file' not in request.POST:
        request.response.status = 400
        return {"error": "No file provided"}
    
    upload = request.POST['file']
    
    # Validate file
    if not hasattr(upload, 'filename') or not upload.filename:
        request.response.status = 400
        return {"error": "Invalid file"}
    
    # Check file size (limit to 10MB)
    if hasattr(upload, 'file'):
        upload.file.seek(0, 2)  # Seek to end
        size = upload.file.tell()
        upload.file.seek(0)  # Reset to beginning
        
        if size > 10 * 1024 * 1024:  # 10MB
            request.response.status = 400
            return {"error": "File too large (max 10MB)"}
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(upload.filename)[1]
    filename = f"{file_id}{file_ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Save file
    with open(filepath, 'wb') as f:
        f.write(upload.file.read())
    
    # Store file metadata
    file_info = {
        "id": file_id,
        "original_name": upload.filename,
        "filename": filename,
        "size": os.path.getsize(filepath),
        "description": description,
        "uploaded_at": datetime.now().isoformat()
    }
    
    request.response.status = 201
    return file_info

@api.get('/files/{file_id}')
def download_file(request, file_id: str) -> dict:
    """Download a file by ID."""
    # In a real app, you'd look up file metadata from database
    filename = f"{file_id}.jpg"  # Simplified for example
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(filepath):
        request.response.status = 404
        return {"error": "File not found"}
    
    # Set response headers for file download
    request.response.content_type = 'application/octet-stream'
    request.response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Return file content
    with open(filepath, 'rb') as f:
        request.response.body = f.read()
    
    return request.response
```

### 3. Complex Data Validation

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, date
import re

@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"

@dataclass
class ContactInfo:
    email: str
    phone: Optional[str] = None
    address: Optional[Address] = None

@dataclass
class Person:
    first_name: str
    last_name: str
    birth_date: date
    contact: ContactInfo

# Validation functions
def validate_email(email: str) -> str:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError("Invalid email format")
    return email.lower()

def validate_phone(phone: str) -> str:
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    if len(digits) != 10:
        raise ValueError("Phone number must be 10 digits")
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

def validate_zip_code(zip_code: str) -> str:
    if not re.match(r'^\d{5}(-\d{4})?$', zip_code):
        raise ValueError("Invalid ZIP code format")
    return zip_code

@api.post('/people')
def create_person(request,
                  first_name: str,
                  last_name: str,
                  birth_date: str,
                  email: str,
                  phone: Optional[str] = None,
                  street: Optional[str] = None,
                  city: Optional[str] = None,
                  state: Optional[str] = None,
                  zip_code: Optional[str] = None) -> dict:
    """Create a person with complex validation."""
    
    errors = {}
    
    # Validate names
    if len(first_name.strip()) < 2:
        errors['first_name'] = 'First name must be at least 2 characters'
    
    if len(last_name.strip()) < 2:
        errors['last_name'] = 'Last name must be at least 2 characters'
    
    # Validate birth date
    try:
        birth_date_obj = datetime.fromisoformat(birth_date).date()
        if birth_date_obj > date.today():
            errors['birth_date'] = 'Birth date cannot be in the future'
        if birth_date_obj < date(1900, 1, 1):
            errors['birth_date'] = 'Birth date cannot be before 1900'
    except ValueError:
        errors['birth_date'] = 'Invalid date format (use YYYY-MM-DD)'
        birth_date_obj = None
    
    # Validate email
    try:
        email = validate_email(email)
    except ValueError as e:
        errors['email'] = str(e)
    
    # Validate phone if provided
    if phone:
        try:
            phone = validate_phone(phone)
        except ValueError as e:
            errors['phone'] = str(e)
    
    # Validate address if provided
    address = None
    if any([street, city, state, zip_code]):
        # If any address field is provided, all required fields must be present
        if not all([street, city, state, zip_code]):
            errors['address'] = 'All address fields (street, city, state, zip_code) are required'
        else:
            try:
                zip_code = validate_zip_code(zip_code)
                address = Address(
                    street=street.strip(),
                    city=city.strip(),
                    state=state.strip().upper(),
                    zip_code=zip_code
                )
            except ValueError as e:
                errors['zip_code'] = str(e)
    
    # Return validation errors
    if errors:
        request.response.status = 400
        return {"error": "Validation failed", "details": errors}
    
    # Create person object
    contact = ContactInfo(
        email=email,
        phone=phone,
        address=address
    )
    
    person = Person(
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        birth_date=birth_date_obj,
        contact=contact
    )
    
    # In a real app, save to database here
    person_dict = {
        "id": str(uuid.uuid4()),
        "first_name": person.first_name,
        "last_name": person.last_name,
        "birth_date": person.birth_date.isoformat(),
        "contact": {
            "email": person.contact.email,
            "phone": person.contact.phone,
            "address": {
                "street": person.contact.address.street,
                "city": person.contact.address.city,
                "state": person.contact.address.state,
                "zip_code": person.contact.address.zip_code,
                "country": person.contact.address.country
            } if person.contact.address else None
        },
        "created_at": datetime.now().isoformat()
    }
    
    request.response.status = 201
    return person_dict
```

### 4. Async Operations with Background Tasks

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pyramid_capstone import api

# Thread pool for background tasks
executor = ThreadPoolExecutor(max_workers=4)

# Task storage (use Redis or database in production)
tasks = {}

def long_running_task(task_id: str, data: dict) -> dict:
    """Simulate a long-running task."""
    import time
    
    # Update task status
    tasks[task_id]["status"] = "processing"
    tasks[task_id]["progress"] = 0
    
    # Simulate work with progress updates
    for i in range(10):
        time.sleep(1)  # Simulate work
        tasks[task_id]["progress"] = (i + 1) * 10
    
    # Complete task
    tasks[task_id]["status"] = "completed"
    tasks[task_id]["result"] = {
        "processed_data": f"Processed: {data}",
        "completed_at": datetime.now().isoformat()
    }
    
    return tasks[task_id]["result"]

@api.post('/tasks')
def create_task(request, task_type: str, data: dict) -> dict:
    """Create a background task."""
    
    if task_type not in ["data_processing", "report_generation"]:
        request.response.status = 400
        return {"error": "Invalid task type"}
    
    task_id = str(uuid.uuid4())
    
    # Initialize task
    tasks[task_id] = {
        "id": task_id,
        "type": task_type,
        "status": "queued",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "result": None
    }
    
    # Submit task to thread pool
    future = executor.submit(long_running_task, task_id, data)
    tasks[task_id]["future"] = future
    
    request.response.status = 202  # Accepted
    return {
        "task_id": task_id,
        "status": "queued",
        "status_url": f"/tasks/{task_id}"
    }

@api.get('/tasks/{task_id}')
def get_task_status(request, task_id: str) -> dict:
    """Get task status and result."""
    
    task = tasks.get(task_id)
    if not task:
        request.response.status = 404
        return {"error": "Task not found"}
    
    # Check if task is done
    if "future" in task and task["future"].done():
        try:
            result = task["future"].result()
            task["status"] = "completed"
            task["result"] = result
        except Exception as e:
            task["status"] = "failed"
            task["error"] = str(e)
        
        # Clean up future reference
        del task["future"]
    
    # Return task info (excluding future object)
    return {
        "id": task["id"],
        "type": task["type"],
        "status": task["status"],
        "progress": task["progress"],
        "created_at": task["created_at"],
        "result": task.get("result"),
        "error": task.get("error")
    }

@api.get('/tasks')
def list_tasks(request, status: Optional[str] = None) -> dict:
    """List all tasks with optional status filter."""
    
    filtered_tasks = []
    for task in tasks.values():
        # Skip future object in response
        task_info = {k: v for k, v in task.items() if k != "future"}
        
        if status is None or task_info["status"] == status:
            filtered_tasks.append(task_info)
    
    return {"tasks": filtered_tasks}
```

### 5. WebSocket Integration

```python
from pyramid_capstone import api
import json

# WebSocket connections storage
websocket_connections = set()

@api.post('/notifications')
def send_notification(request, message: str, notification_type: str = "info") -> dict:
    """Send notification to all connected WebSocket clients."""
    
    notification = {
        "type": notification_type,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    # Send to all connected WebSocket clients
    disconnected = set()
    for ws in websocket_connections:
        try:
            ws.send(json.dumps(notification))
        except:
            # Connection is closed, mark for removal
            disconnected.add(ws)
    
    # Remove disconnected clients
    websocket_connections -= disconnected
    
    return {
        "message": "Notification sent",
        "recipients": len(websocket_connections),
        "notification": notification
    }

@api.get('/notifications/stats')
def get_notification_stats(request) -> dict:
    """Get notification system statistics."""
    return {
        "connected_clients": len(websocket_connections),
        "server_time": datetime.now().isoformat()
    }

# WebSocket handler (separate from api decorators)
def websocket_view(request):
    """Handle WebSocket connections."""
    ws = request.environ.get('wsgi.websocket')
    if not ws:
        request.response.status = 400
        return {"error": "WebSocket connection required"}
    
    # Add to connections
    websocket_connections.add(ws)
    
    try:
        # Send welcome message
        welcome = {
            "type": "welcome",
            "message": "Connected to notification service",
            "timestamp": datetime.now().isoformat()
        }
        ws.send(json.dumps(welcome))
        
        # Keep connection alive
        while True:
            message = ws.receive()
            if message is None:
                break
            
            # Echo received messages (for testing)
            echo = {
                "type": "echo",
                "message": f"Received: {message}",
                "timestamp": datetime.now().isoformat()
            }
            ws.send(json.dumps(echo))
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    
    finally:
        # Remove from connections
        websocket_connections.discard(ws)
    
    return {}
```

### 6. API Versioning

```python
from pyramid_capstone import api

# Version 1 API
@api.get('/v1/users/{user_id}')
def get_user_v1(request, user_id: int) -> dict:
    """Get user (v1 format)."""
    user = get_user_from_db(user_id)
    if not user:
        request.response.status = 404
        return {"error": "User not found"}
    
    # V1 format - simple structure
    return {
        "id": user.id,
        "name": user.username,
        "email": user.email
    }

# Version 2 API
@api.get('/v2/users/{user_id}')
def get_user_v2(request, user_id: int, include_profile: bool = False) -> dict:
    """Get user (v2 format with enhanced features)."""
    user = get_user_from_db(user_id)
    if not user:
        request.response.status = 404
        return {"error": "User not found"}
    
    # V2 format - enhanced structure
    result = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "is_active": user.is_active,
        "metadata": {
            "version": "2.0",
            "last_updated": user.updated_at.isoformat()
        }
    }
    
    # Optional profile inclusion
    if include_profile and user.profile:
        result["profile"] = {
            "bio": user.profile.bio,
            "avatar_url": user.profile.avatar_url,
            "location": user.profile.location
        }
    
    return result

# Version negotiation through headers
@api.get('/users/{user_id}')
def get_user_versioned(request, user_id: int) -> dict:
    """Get user with version negotiation."""
    
    # Check Accept header for version
    accept_header = request.headers.get('Accept', '')
    
    if 'application/vnd.api.v2+json' in accept_header:
        return get_user_v2(request, user_id)
    else:
        # Default to v1
        return get_user_v1(request, user_id)
```

## Integration Examples

### SQLAlchemy Integration

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from pyramid_capstone import api

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(String, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    author = relationship("User", back_populates="posts")

@api.get('/users/{user_id}/posts')
def get_user_posts(request, user_id: int, page: int = 1, per_page: int = 10) -> dict:
    """Get user posts with SQLAlchemy."""
    
    # Query with eager loading to avoid N+1 queries
    posts_query = (request.dbsession.query(Post)
                   .filter_by(author_id=user_id)
                   .order_by(Post.created_at.desc()))
    
    # Get total count
    total = posts_query.count()
    
    # Apply pagination
    posts = (posts_query
             .offset((page - 1) * per_page)
             .limit(per_page)
             .all())
    
    return {
        "posts": [
            {
                "id": post.id,
                "title": post.title,
                "content": post.content[:200] + "..." if len(post.content) > 200 else post.content,
                "created_at": post.created_at.isoformat()
            }
            for post in posts
        ],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "has_next": (page * per_page) < total,
            "has_prev": page > 1
        }
    }
```

These examples demonstrate the flexibility and power of `pyramid-capstone` for building various types of APIs. Each pattern can be adapted and combined to meet your specific requirements.

For more comprehensive examples, check out the [Blog API example](https://github.com/tomas_correa/pyramid-capstone/tree/main/examples/blog_api) in the repository.
