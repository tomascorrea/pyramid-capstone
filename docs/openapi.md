# OpenAPI Documentation

`pyramid-capstone` provides automatic OpenAPI 3.0 documentation generation for your API endpoints using **pycornmarsh**. This means you get interactive API documentation (Swagger UI) without writing any additional code!

## Quick Start

Enable OpenAPI documentation with a single configuration call:

```python
from pyramid.config import Configurator

def main(global_config, **settings):
    config = Configurator(settings=settings)
    
    # Include pyramid-capstone
    config.include('pyramid_capstone')
    
    # Enable OpenAPI documentation
    config.capstone_enable_openapi_docs(
        title="My API",
        version="1.0.0",
        description="A comprehensive API with automatic documentation"
    )
    
    # Scan for your API endpoints
    config.scan()
    
    return config.make_wsgi_app()
```

That's it! Your API now has:

- **OpenAPI JSON**: `/api/v1/openapi.json` - Machine-readable API specification
- **Swagger UI**: `/api/v1/api-explorer` - Interactive API documentation

## Configuration Options

### Basic Configuration

```python
config.capstone_enable_openapi_docs(
    title="My API",           # Required: API title
    version="1.0.0",          # Required: API version
)
```

### Full Configuration

```python
config.capstone_enable_openapi_docs(
    title="Task Management API",
    version="1.0.0",
    description="A complete task management system with user assignment, "
                "categories, and priority tracking.",
    api_version="v1",         # Optional: URL version prefix (default: "v1")
    api_prefix="/api",        # Optional: URL prefix (default: "/api")
    security_scheme={         # Optional: Security scheme for authenticated endpoints
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
)
```

### Custom URL Paths

Change where the OpenAPI documentation is served:

```python
# Serve at /docs/v2/openapi.json and /docs/v2/api-explorer
config.capstone_enable_openapi_docs(
    title="My API v2",
    version="2.0.0",
    api_version="v2",
    api_prefix="/docs"
)
```

### Adding Security Schemes

Document authentication requirements in your OpenAPI spec:

```python
# Bearer Token (JWT)
config.capstone_enable_openapi_docs(
    title="Secure API",
    version="1.0.0",
    security_scheme={
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
)

# API Key in Header
config.capstone_enable_openapi_docs(
    title="API Key Protected API",
    version="1.0.0",
    security_scheme={
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
)

# OAuth 2.0
config.capstone_enable_openapi_docs(
    title="OAuth Protected API",
    version="1.0.0",
    security_scheme={
        "OAuth2": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "https://example.com/oauth/authorize",
                    "tokenUrl": "https://example.com/oauth/token",
                    "scopes": {
                        "read": "Read access",
                        "write": "Write access"
                    }
                }
            }
        }
    }
)

# Multiple Security Schemes
config.capstone_enable_openapi_docs(
    title="Multi-Auth API",
    version="1.0.0",
    security_scheme={
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }
)
```

When you define a security scheme, it will appear in the Swagger UI, allowing users to:
- See which endpoints require authentication
- Test authenticated endpoints by providing credentials
- Understand the authentication mechanism

## What Gets Documented?

`pyramid-capstone` automatically documents:

### ✅ Endpoints

All `@api` decorated endpoints are automatically included:

```python
from pyramid_capstone import api

@api.get('/users')
def list_users(request) -> List[User]:
    """Get all users in the system."""
    return users
```

This generates:
- **Path**: `/users`
- **Method**: `GET`
- **Summary**: First line of docstring
- **Description**: Full docstring
- **Response Schema**: Automatically generated from `List[User]` return type

### 📋 Request Parameters

Parameters are automatically documented with their types and requirements:

```python
@api.post('/tasks')
def create_task(request, 
                title: str,                    # Required parameter
                description: Optional[str] = None,  # Optional parameter
                priority: str = "medium") -> Task:  # Optional with default
    """Create a new task."""
    ...
```

Generates documentation for:
- **Required**: `title` (string, required)
- **Optional**: `description` (string, optional)
- **With Default**: `priority` (string, optional, default: "medium")

### 📤 Request Body Schemas

POST/PUT/PATCH request bodies are automatically documented:

```python
@api.post('/users')
def create_user(request, name: str, email: str, age: int = 25) -> User:
    """Create a new user."""
    ...
```

Generates OpenAPI schema:

```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "email": {"type": "string"},
    "age": {"type": "integer", "default": 25}
  },
  "required": ["name", "email"]
}
```

### 📥 Response Schemas

Return types are automatically converted to OpenAPI schemas:

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class User:
    id: str
    name: str
    email: str
    age: Optional[int] = None

@api.get('/users/{user_id}')
def get_user(request, user_id: str) -> User:
    """Get a user by ID."""
    ...
```

Generates complete response schema with all fields, types, and optional indicators.

### 📊 Complex Types

Nested objects and lists are fully documented:

```python
@dataclass
class Comment:
    id: str
    content: str
    author: User  # Nested object

@dataclass
class Post:
    id: str
    title: str
    comments: List[Comment]  # List of objects

@api.get('/posts/{post_id}')
def get_post(request, post_id: str) -> Post:
    """Get a post with its comments."""
    ...
```

All nested schemas are automatically generated and linked in the OpenAPI spec.

## Using the Interactive Documentation

Once you've enabled OpenAPI documentation, visit the Swagger UI:

```
http://localhost:6543/api/v1/api-explorer
```

### Features:

1. **Browse Endpoints**: See all your API endpoints organized by path
2. **View Schemas**: Examine request and response data structures
3. **Try It Out**: Test your API directly from the browser
4. **See Examples**: Auto-generated example requests and responses

### Testing Endpoints

1. Click on an endpoint to expand it
2. Click "Try it out" button
3. Fill in parameters
4. Click "Execute"
5. See the actual response from your API

## Accessing the OpenAPI JSON

The raw OpenAPI specification is available at:

```
http://localhost:6543/api/v1/openapi.json
```

You can use this with:

- **Code Generators**: Generate client SDKs in various languages
- **API Testing Tools**: Import into Postman, Insomnia, etc.
- **Documentation Generators**: Create custom documentation
- **Validation Tools**: Validate requests/responses against the spec

## Complete Example

Here's a complete example of an API with OpenAPI documentation:

```python
# app.py
from pyramid.config import Configurator
from pyramid_capstone import api
from dataclasses import dataclass
from typing import List, Optional

# Data models
@dataclass
class Task:
    id: str
    title: str
    description: Optional[str]
    completed: bool = False

# In-memory storage
tasks_db = {}

# API endpoints
@api.get('/tasks')
def list_tasks(request) -> List[Task]:
    """
    List all tasks in the system.
    
    Returns a list of all tasks with their current status.
    """
    return list(tasks_db.values())

@api.get('/tasks/{task_id}')
def get_task(request, task_id: str) -> Task:
    """Get a specific task by its ID."""
    task = tasks_db.get(task_id)
    if not task:
        request.response.status = 404
        return {"error": "Task not found"}
    return task

@api.post('/tasks')
def create_task(request, 
                title: str,
                description: Optional[str] = None) -> Task:
    """
    Create a new task.
    
    Provide a title (required) and optional description.
    Returns the created task with a generated ID.
    """
    task_id = str(len(tasks_db) + 1)
    task = Task(
        id=task_id,
        title=title,
        description=description
    )
    tasks_db[task_id] = task
    request.response.status = 201
    return task

@api.put('/tasks/{task_id}')
def update_task(request,
                task_id: str,
                title: Optional[str] = None,
                description: Optional[str] = None,
                completed: Optional[bool] = None) -> Task:
    """
    Update an existing task.
    
    All fields are optional - only provided fields will be updated.
    """
    task = tasks_db.get(task_id)
    if not task:
        request.response.status = 404
        return {"error": "Task not found"}
    
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if completed is not None:
        task.completed = completed
    
    return task

@api.delete('/tasks/{task_id}')
def delete_task(request, task_id: str) -> dict:
    """Delete a task by ID."""
    if task_id not in tasks_db:
        request.response.status = 404
        return {"error": "Task not found"}
    
    del tasks_db[task_id]
    return {"message": "Task deleted successfully"}

# Application setup
def main(global_config, **settings):
    config = Configurator(settings=settings)
    
    # Include pyramid-capstone
    config.include('pyramid_capstone')
    
    # Enable OpenAPI documentation
    config.capstone_enable_openapi_docs(
        title="Task API",
        version="1.0.0",
        description="A simple task management API demonstrating "
                    "pyramid-capstone with automatic OpenAPI documentation.",
        api_version="v1",
        api_prefix="/api"
    )
    
    # Scan for API endpoints
    config.scan()
    
    return config.make_wsgi_app()

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    app = main({})
    server = make_server('0.0.0.0', 6543, app)
    print("API running on http://localhost:6543")
    print("OpenAPI docs: http://localhost:6543/api/v1/api-explorer")
    print("OpenAPI JSON: http://localhost:6543/api/v1/openapi.json")
    server.serve_forever()
```

Run it:

```bash
python app.py
```

Then visit:
- **API Explorer**: http://localhost:6543/api/v1/api-explorer
- **OpenAPI Spec**: http://localhost:6543/api/v1/openapi.json

## Best Practices

### 1. Write Good Docstrings

Docstrings become your API documentation:

```python
@api.post('/users')
def create_user(request, name: str, email: str) -> User:
    """
    Create a new user account.
    
    This endpoint creates a new user with the provided name and email.
    The email must be unique across all users.
    
    Returns:
        The created user object with a generated ID.
    
    Errors:
        400: Invalid email format or duplicate email
        500: Server error during user creation
    """
    ...
```

### 2. Use Type Hints Consistently

Type hints drive schema generation:

```python
# ✅ Good: Clear types
def create_task(request, title: str, priority: int) -> Task:
    ...

# ❌ Bad: Missing types
def create_task(request, title, priority):
    ...
```

### 3. Use Dataclasses for Complex Types

Dataclasses generate clean schemas:

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class CreateTaskRequest:
    title: str
    description: Optional[str]
    priority: int = 1

@dataclass
class TaskResponse:
    id: str
    title: str
    description: Optional[str]
    priority: int
    created_at: str

@api.post('/tasks')
def create_task(request, **data) -> TaskResponse:
    """Create a task with structured data."""
    ...
```

### 4. Document Error Responses

Add error cases in docstrings:

```python
@api.get('/users/{user_id}')
def get_user(request, user_id: str) -> User:
    """
    Get a user by ID.
    
    Returns:
        200: User object
        404: User not found
        500: Server error
    """
    user = get_user_from_db(user_id)
    if not user:
        request.response.status = 404
        return {"error": "User not found"}
    return user
```

### 5. Group Related Endpoints

Use consistent naming for related endpoints:

```python
# User management
@api.get('/users')
@api.get('/users/{user_id}')
@api.post('/users')
@api.put('/users/{user_id}')
@api.delete('/users/{user_id}')

# Task management
@api.get('/tasks')
@api.get('/tasks/{task_id}')
@api.post('/tasks')
```

## Troubleshooting

### OpenAPI Endpoint Returns 404

Make sure you called `capstone_enable_openapi_docs()` before `config.scan()`:

```python
# ✅ Correct order
config.include('pyramid_capstone')
config.capstone_enable_openapi_docs(...)
config.scan()

# ❌ Wrong order
config.include('pyramid_capstone')
config.scan()
config.capstone_enable_openapi_docs(...)  # Too late!
```

### Schemas Not Showing

Ensure you're using type hints:

```python
# ✅ Type hints present
def get_user(request, user_id: str) -> User:
    ...

# ❌ No type hints
def get_user(request, user_id):
    ...
```

### Endpoints Missing from Documentation

Check that all endpoints have the `pcm_show` metadata set (this is automatic with default "v1" version). If you're using a custom version, specify it:

```python
config.capstone_enable_openapi_docs(
    title="My API",
    version="1.0.0",
    api_version="v2"  # Must match your endpoint versions
)
```

## Next Steps

- **[Security](security.md)** - Add authentication to your documented API
- **[Examples](examples.md)** - See more complex OpenAPI examples
- **[Tutorial](tutorial.md)** - Build a complete API with documentation

## External Tools

Use the generated OpenAPI spec with:

- **[Swagger Editor](https://editor.swagger.io/)** - Edit and validate OpenAPI specs
- **[OpenAPI Generator](https://openapi-generator.tech/)** - Generate client SDKs
- **[Postman](https://www.postman.com/)** - Import and test APIs
- **[Insomnia](https://insomnia.rest/)** - REST client with OpenAPI support
- **[ReDoc](https://redocly.github.io/redoc/)** - Alternative documentation UI

