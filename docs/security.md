# Security Integration

`pyramid-type-hinted-api` integrates seamlessly with Pyramid's powerful security system, allowing you to protect your API endpoints with authentication and authorization.

## Quick Start

Add the `permission` parameter to any endpoint decorator:

```python
from pyramid_type_hinted_api import th_api

@th_api.get('/admin/users', permission='admin')
def list_users_admin(request) -> list:
    """Only users with 'admin' permission can access this."""
    return get_all_users()

@th_api.post('/posts', permission='create_post')
def create_post(request, title: str, content: str) -> dict:
    """Only authenticated users with 'create_post' permission."""
    return create_new_post(title, content)
```

## Setting Up Authentication

### 1. Basic Authentication Setup

Here's a complete example with session-based authentication:

```python
from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow, Everyone, Authenticated
from pyramid_type_hinted_api import th_api

class RootACL:
    """Root Access Control List."""
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, Authenticated, 'create'),
        (Allow, 'group:admins', 'admin'),
    ]

def main(global_config, **settings):
    config = Configurator(
        settings=settings,
        root_factory=lambda request: RootACL()
    )
    
    # Set up authentication and authorization
    config.set_authentication_policy(SessionAuthenticationPolicy())
    config.set_authorization_policy(ACLAuthorizationPolicy())
    
    # Include pyramid-type-hinted-api
    config.include('pyramid_type_hinted_api')
    config.scan()
    
    return config.make_wsgi_app()
```

### 2. JWT Authentication

For API-first applications, JWT tokens are often preferred:

```python
from pyramid_jwt import create_jwt_authentication_policy

def main(global_config, **settings):
    config = Configurator(settings=settings)
    
    # JWT Authentication
    jwt_policy = create_jwt_authentication_policy(
        private_key='your-secret-key',
        algorithm='HS256',
        expiration=3600,  # 1 hour
        auth_type='Bearer'
    )
    
    config.set_authentication_policy(jwt_policy)
    config.set_authorization_policy(ACLAuthorizationPolicy())
    
    config.include('pyramid_type_hinted_api')
    config.scan()
    
    return config.make_wsgi_app()
```

## Protected Endpoints

### Basic Permission Checking

```python
@th_api.get('/profile', permission='view')
def get_profile(request) -> dict:
    """Any authenticated user can view their profile."""
    user_id = request.authenticated_userid
    return {"user_id": user_id, "profile": get_user_profile(user_id)}

@th_api.post('/admin/users', permission='admin')
def create_user_admin(request, username: str, email: str) -> dict:
    """Only admins can create users."""
    return create_user(username, email)

@th_api.delete('/posts/{post_id}', permission='delete_post')
def delete_post(request, post_id: int) -> dict:
    """Only users with delete_post permission."""
    delete_post_by_id(post_id)
    return {"message": "Post deleted"}
```

### Dynamic Permissions

For more complex authorization, you can use dynamic permissions:

```python
from pyramid.security import has_permission

@th_api.get('/posts/{post_id}')
def get_post(request, post_id: int) -> dict:
    """Public posts are viewable by everyone, private posts need permission."""
    post = get_post_by_id(post_id)
    
    if post.is_private:
        # Check if user has permission to view private posts
        if not has_permission('view_private', request.context, request):
            request.response.status = 403
            return {"error": "Access denied"}
    
    return post.to_dict()

@th_api.put('/posts/{post_id}')
def update_post(request, post_id: int, title: str, content: str) -> dict:
    """Users can only edit their own posts, unless they're admins."""
    post = get_post_by_id(post_id)
    user_id = request.authenticated_userid
    
    # Check ownership or admin permission
    if post.author_id != user_id and not has_permission('admin', request.context, request):
        request.response.status = 403
        return {"error": "You can only edit your own posts"}
    
    return update_post_content(post_id, title, content)
```

## Authentication Endpoints

Create login/logout endpoints to manage authentication:

```python
from pyramid.security import remember, forget
import bcrypt

# In-memory user store (use a database in production)
USERS = {
    "alice": {
        "password": bcrypt.hashpw(b"secret123", bcrypt.gensalt()),
        "groups": ["users"]
    },
    "admin": {
        "password": bcrypt.hashpw(b"admin123", bcrypt.gensalt()),
        "groups": ["users", "admins"]
    }
}

@th_api.post('/auth/login')
def login(request, username: str, password: str) -> dict:
    """Authenticate user and create session."""
    user = USERS.get(username)
    
    if not user or not bcrypt.checkpw(password.encode(), user["password"]):
        request.response.status = 401
        return {"error": "Invalid credentials"}
    
    # Create authentication headers
    headers = remember(request, username)
    request.response.headerlist.extend(headers)
    
    return {
        "message": "Login successful",
        "user": username,
        "groups": user["groups"]
    }

@th_api.post('/auth/logout')
def logout(request) -> dict:
    """Logout user and clear session."""
    headers = forget(request)
    request.response.headerlist.extend(headers)
    return {"message": "Logout successful"}

@th_api.get('/auth/me', permission='view')
def get_current_user(request) -> dict:
    """Get current authenticated user info."""
    username = request.authenticated_userid
    user = USERS.get(username, {})
    
    return {
        "username": username,
        "groups": user.get("groups", [])
    }
```

## Advanced Security Patterns

### Role-Based Access Control (RBAC)

```python
from pyramid.security import Allow, Deny, Everyone, Authenticated

class BlogACL:
    """Access Control List for blog resources."""
    def __init__(self, request):
        self.request = request
        
    @property
    def __acl__(self):
        # Base permissions
        acl = [
            (Allow, Everyone, 'view_public'),
            (Allow, Authenticated, 'view_private'),
            (Allow, Authenticated, 'create_post'),
            (Allow, 'group:moderators', 'moderate'),
            (Allow, 'group:admins', 'admin'),
        ]
        
        # Dynamic permissions based on context
        if hasattr(self, 'post_id'):
            post = get_post_by_id(self.post_id)
            if post:
                # Post authors can edit their own posts
                acl.append((Allow, f'user:{post.author_id}', 'edit_post'))
        
        return acl

# Use in configuration
def main(global_config, **settings):
    config = Configurator(
        settings=settings,
        root_factory=BlogACL
    )
    # ... rest of configuration
```

### API Key Authentication

```python
import secrets
from pyramid.authentication import CallbackAuthenticationPolicy

# API key storage (use database in production)
API_KEYS = {
    "sk_test_123": {"user_id": "alice", "permissions": ["read", "write"]},
    "sk_prod_456": {"user_id": "admin", "permissions": ["read", "write", "admin"]},
}

class APIKeyAuthenticationPolicy(CallbackAuthenticationPolicy):
    def unauthenticated_userid(self, request):
        """Extract API key from Authorization header."""
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        return None
    
    def callback(self, userid, request):
        """Validate API key and return user groups."""
        key_data = API_KEYS.get(userid)
        if key_data:
            return [f"permission:{perm}" for perm in key_data["permissions"]]
        return None

# Protected endpoint with API key
@th_api.get('/api/data', permission='read')
def get_api_data(request) -> dict:
    """Access with: Authorization: Bearer sk_test_123"""
    api_key = request.authenticated_userid
    key_data = API_KEYS.get(api_key, {})
    
    return {
        "data": "sensitive information",
        "user_id": key_data.get("user_id"),
        "permissions": key_data.get("permissions", [])
    }
```

### Rate Limiting

```python
from functools import wraps
from time import time
from collections import defaultdict

# Simple in-memory rate limiter (use Redis in production)
rate_limit_storage = defaultdict(list)

def rate_limit(max_requests: int = 100, window_seconds: int = 3600):
    """Rate limiting decorator."""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Get client identifier (IP or user ID)
            client_id = request.authenticated_userid or request.client_addr
            current_time = time()
            
            # Clean old requests
            rate_limit_storage[client_id] = [
                req_time for req_time in rate_limit_storage[client_id]
                if current_time - req_time < window_seconds
            ]
            
            # Check rate limit
            if len(rate_limit_storage[client_id]) >= max_requests:
                request.response.status = 429
                return {"error": "Rate limit exceeded"}
            
            # Record this request
            rate_limit_storage[client_id].append(current_time)
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

# Apply rate limiting
@th_api.post('/api/expensive-operation', permission='create')
@rate_limit(max_requests=10, window_seconds=3600)  # 10 requests per hour
def expensive_operation(request, data: str) -> dict:
    """Rate-limited endpoint."""
    return perform_expensive_operation(data)
```

## Security Best Practices

### 1. Input Validation

Always validate and sanitize input data:

```python
import re
from html import escape

@th_api.post('/posts')
def create_post(request, title: str, content: str, permission='create_post') -> dict:
    """Create a post with input validation."""
    
    # Validate title length
    if len(title.strip()) < 3:
        request.response.status = 400
        return {"error": "Title must be at least 3 characters"}
    
    if len(title) > 200:
        request.response.status = 400
        return {"error": "Title must be less than 200 characters"}
    
    # Sanitize HTML content
    content = escape(content)
    
    # Validate content
    if len(content.strip()) < 10:
        request.response.status = 400
        return {"error": "Content must be at least 10 characters"}
    
    return create_new_post(title.strip(), content)
```

### 2. CORS Configuration

For browser-based applications:

```python
def main(global_config, **settings):
    config = Configurator(settings=settings)
    
    # CORS settings
    config.add_settings({
        'cors.preflight_maxage': '3600',
        'cors.origins': 'https://yourdomain.com',
        'cors.credentials': 'true'
    })
    
    config.include('pyramid_cors')
    config.include('pyramid_type_hinted_api')
    config.scan()
    
    return config.make_wsgi_app()
```

### 3. HTTPS Enforcement

```python
from pyramid.events import NewRequest

def require_https(event):
    """Redirect HTTP requests to HTTPS."""
    request = event.request
    if request.scheme != 'https' and not request.registry.settings.get('debug'):
        raise HTTPSRequired()

def main(global_config, **settings):
    config = Configurator(settings=settings)
    
    # Enforce HTTPS in production
    if not settings.get('debug'):
        config.add_subscriber(require_https, NewRequest)
    
    # ... rest of configuration
```

### 4. Security Headers

```python
from pyramid.events import NewResponse

def add_security_headers(event):
    """Add security headers to all responses."""
    response = event.response
    response.headers.update({
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'"
    })

def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.add_subscriber(add_security_headers, NewResponse)
    # ... rest of configuration
```

## Testing Secured Endpoints

Test your secured endpoints properly:

```python
import pytest
from pyramid.testing import DummyRequest
from pyramid.security import remember

def test_protected_endpoint_requires_auth(pyramid_config):
    """Test that protected endpoints require authentication."""
    request = DummyRequest()
    
    # Should fail without authentication
    response = get_profile(request)
    assert request.response.status_int == 403

def test_protected_endpoint_with_auth(pyramid_config):
    """Test protected endpoint with valid authentication."""
    request = DummyRequest()
    
    # Simulate authenticated user
    request.authenticated_userid = 'alice'
    
    response = get_profile(request)
    assert response['user_id'] == 'alice'

def test_admin_endpoint_requires_admin_permission(pyramid_config):
    """Test that admin endpoints require admin permission."""
    request = DummyRequest()
    request.authenticated_userid = 'regular_user'
    
    # Mock has_permission to return False for non-admin
    with patch('pyramid.security.has_permission', return_value=False):
        response = create_user_admin(request, 'newuser', 'new@example.com')
        assert request.response.status_int == 403
```

## Common Security Patterns

### Resource-Based Permissions

```python
@th_api.get('/posts/{post_id}', permission='view_post')
def get_post(request, post_id: int) -> dict:
    """Permission is checked against the specific post resource."""
    # Pyramid will check 'view_post' permission against the post context
    pass

@th_api.put('/posts/{post_id}', permission='edit_post')
def update_post(request, post_id: int, title: str) -> dict:
    """Only users who can edit this specific post."""
    pass
```

### Conditional Security

```python
@th_api.get('/posts/{post_id}')
def get_post_conditional(request, post_id: int) -> dict:
    """Apply security conditionally based on post visibility."""
    post = get_post_by_id(post_id)
    
    if post.is_private:
        # Check authentication for private posts
        if not request.authenticated_userid:
            request.response.status = 401
            return {"error": "Authentication required"}
        
        # Check if user can view this private post
        if not can_view_private_post(request.authenticated_userid, post):
            request.response.status = 403
            return {"error": "Access denied"}
    
    return post.to_dict()
```

Security is a crucial aspect of API development. The `pyramid-type-hinted-api` library makes it easy to integrate with Pyramid's robust security system while maintaining clean, readable code.

For more examples of security implementations, see our [Examples](examples.md) guide.
