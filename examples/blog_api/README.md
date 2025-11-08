# Blog API Example

This is a comprehensive example application demonstrating the `pyramid-capstone` library with a complete blog API featuring users, posts, comments, and categories.

## Features Demonstrated

### 🎯 Core Features
- **Type-hinted API endpoints** with automatic validation and serialization
- **CRUD operations** for all entities (Create, Read, Update, Delete)
- **Complex return types** including nested objects and lists
- **Parameter injection** from URL paths, query parameters, and JSON bodies
- **Optional parameters** with default values
- **Error handling** with proper HTTP status codes

### 🏗️ Real-World Patterns
- **Pagination** and filtering for list endpoints
- **Nested relationships** between entities (posts have authors and categories)
- **Data validation** with meaningful error messages
- **RESTful API design** following best practices
- **Statistics and analytics** endpoints

## API Endpoints

### Health & Info
- `GET /` - API documentation and endpoint listing
- `GET /health` - Health check with system statistics

### Users
- `GET /users` - List all users
- `GET /users/{user_id}` - Get user by ID
- `POST /users` - Create new user
- `PUT /users/{user_id}` - Update user
- `DELETE /users/{user_id}` - Delete user
- `GET /users/{user_id}/posts` - Get posts by user (with pagination)

### Categories
- `GET /categories` - List all categories
- `GET /categories/{category_id}` - Get category by ID
- `POST /categories` - Create new category

### Posts
- `GET /posts` - List posts with filtering and pagination
  - Query params: `status`, `category_id`, `author_id`, `page`, `per_page`
- `GET /posts/{post_id}` - Get post by ID
  - Query params: `include_comments`
- `POST /posts` - Create new post
- `PUT /posts/{post_id}` - Update post
- `DELETE /posts/{post_id}` - Delete post

### Comments
- `GET /posts/{post_id}/comments` - List comments for a post
- `POST /posts/{post_id}/comments` - Create comment on post
- `GET /comments/{comment_id}` - Get comment by ID
- `DELETE /comments/{comment_id}` - Delete comment

### Statistics
- `GET /stats` - Get blog statistics (user count, post count, etc.)

## Running the Example

### Prerequisites
Make sure you have the `pyramid-capstone` library installed with development dependencies:

```bash
# Install with development dependencies for OpenAPI documentation
poetry install --with dev
```

### Start the Server
```bash
# From the examples/blog_api directory
cd examples/blog_api
pserve development.ini

# The server will start on http://localhost:6543
```

### Explore the API
1. **Visit the root endpoint**: http://localhost:6543/
   - See API information and documentation links
2. **Interactive API Documentation**:
   - **Swagger UI**: http://localhost:6543/swagger-ui/
   - **ReDoc**: http://localhost:6543/redoc/
   - **OpenAPI JSON**: http://localhost:6543/openapi.json
3. **Quick endpoints to try**:
   - **Health check**: http://localhost:6543/health
   - **Statistics**: http://localhost:6543/stats
   - **List users**: http://localhost:6543/users
   - **List posts**: http://localhost:6543/posts

## Example Usage

### Create a User
```bash
curl -X POST http://localhost:6543/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "full_name": "Alice Johnson",
    "bio": "Software developer and blogger"
  }'
```

### Create a Post
```bash
curl -X POST http://localhost:6543/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Blog Post",
    "content": "This is the content of my first blog post...",
    "excerpt": "A brief introduction to my blog",
    "author_id": 1,
    "category_id": 1,
    "status": "published"
  }'
```

### List Posts with Filtering
```bash
# Get published posts, page 1, 5 per page
curl "http://localhost:6543/posts?status=published&page=1&per_page=5"

# Get posts by specific author
curl "http://localhost:6543/posts?author_id=1"

# Get posts in specific category
curl "http://localhost:6543/posts?category_id=2"
```

### Add a Comment
```bash
curl -X POST http://localhost:6543/posts/1/comments \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Great post! Very informative.",
    "author_id": 2
  }'
```

## Data Models

The example includes several data models that demonstrate different type hint patterns:

### User
```python
@dataclass
class User:
    id: int
    username: str
    email: str
    full_name: str
    bio: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
```

### Post
```python
@dataclass
class Post:
    id: int
    title: str
    slug: str
    content: str
    excerpt: Optional[str] = None
    author_id: int
    category_id: Optional[int] = None
    status: PostStatus = PostStatus.DRAFT
    created_at: Optional[datetime] = None
    # ... and more fields
```

### Complex Types
- **Enums**: `PostStatus` for post publication status
- **Optional fields**: Many fields are optional with sensible defaults
- **Nested objects**: Posts include author and category information
- **Lists**: Comments are returned as lists with full author details

## Sample Data

The example starts with sample data including:
- **3 users**: John Doe, Jane Smith, Bob Wilson
- **3 categories**: Technology, Python, Web Development
- **3 posts**: Various topics with different statuses
- **3 comments**: Sample discussions on posts

## Code Structure

```
examples/blog_api/
├── __init__.py          # Package documentation
├── __main__.py          # Module entry point
├── app.py              # Pyramid application configuration
├── models.py           # Data models and type definitions
├── data_store.py       # In-memory data storage
├── views.py            # API endpoints using api decorators
└── README.md           # This documentation
```

## Key Implementation Highlights

### Type-Safe Endpoints
```python
@api.get('/posts/{post_id}')
def get_post(request, post_id: int, include_comments: bool = False) -> Post:
    """Get a post by ID with optional comments."""
    # Implementation automatically validates post_id as int
    # and include_comments as bool from query parameters
```

### Complex Parameter Handling
```python
@api.get('/posts')
def list_posts(request, status: Optional[str] = None, 
               category_id: Optional[int] = None,
               page: int = 1, per_page: int = 10) -> dict:
    """List posts with filtering and pagination."""
    # All parameters are automatically extracted and validated
```

### Error Handling
```python
@api.get('/users/{user_id}')
def get_user(request, user_id: int) -> User:
    """Get a user by ID."""
    user = blog_store.get_user(user_id)
    if not user:
        request.response.status = 404
        return {'error': 'User not found'}
    return user
```

This example demonstrates how `pyramid-capstone` makes it easy to build robust, type-safe REST APIs with minimal boilerplate code while maintaining full compatibility with Pyramid's ecosystem.
