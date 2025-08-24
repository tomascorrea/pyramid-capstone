# Getting Started

This guide will help you get up and running with `pyramid-capstone` in just a few minutes.

## Installation

Install the package using pip:

```bash
poetry add pyramid-capstone
```

Or if you're using pip:

```bash
pip install pyramid-capstone
```

## Requirements

- Python 3.8+
- Pyramid 2.0+
- Cornice (automatically installed as a dependency)

## Your First API

Let's create a simple API to demonstrate the basic concepts.

### 1. Create a Basic Pyramid Application

Create a file called `app.py`:

```python
from pyramid.config import Configurator
from pyramid_capstone import th_api

# Your API endpoints
@th_api.get('/hello')
def hello_world(request) -> dict:
    """A simple hello world endpoint."""
    return {"message": "Hello, World!"}

@th_api.get('/hello/{name}')
def hello_name(request, name: str) -> dict:
    """Greet someone by name."""
    return {"message": f"Hello, {name}!"}

@th_api.post('/users')
def create_user(request, name: str, email: str, age: int = 25) -> dict:
    """Create a new user with automatic validation."""
    return {
        "message": "User created successfully",
        "user": {
            "name": name,
            "email": email, 
            "age": age
        }
    }

# Application setup
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
    print("Server running on http://localhost:6543")
    server.serve_forever()
```

### 2. Run Your Application

```bash
python app.py
```

Your API is now running on `http://localhost:6543`!

### 3. Test Your Endpoints

Try these requests:

```bash
# Simple GET request
curl http://localhost:6543/hello

# GET with path parameter
curl http://localhost:6543/hello/Alice

# POST with JSON body (automatic validation)
curl -X POST http://localhost:6543/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com", "age": 30}'

# POST with missing optional parameter (uses default)
curl -X POST http://localhost:6543/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane", "email": "jane@example.com"}'
```

## What Just Happened?

Let's break down what `pyramid-capstone` did for you:

### 🔍 Automatic Parameter Extraction

```python
@th_api.get('/hello/{name}')
def hello_name(request, name: str) -> dict:
    # name is automatically extracted from the URL path
    # and validated as a string
```

### ✅ Request Validation

```python
@th_api.post('/users')
def create_user(request, name: str, email: str, age: int = 25) -> dict:
    # Parameters are automatically extracted from JSON body
    # name and email are required (will return 400 if missing)
    # age is optional with default value 25
    # age will be validated as integer (400 if not a number)
```

### 📝 Response Serialization

```python
def hello_world(request) -> dict:
    return {"message": "Hello, World!"}
    # Return value is automatically serialized to JSON
    # Content-Type header is set to application/json
```

## Configuration Options

### Using with an INI File

For production applications, you'll typically use an INI configuration file:

Create `development.ini`:

```ini
[app:main]
use = egg:your_app

pyramid.reload_templates = true
pyramid.debug_authorization = false
pyramid.debug_notfound = false
pyramid.debug_routematch = false
pyramid.default_locale_name = en

[server:main]
use = egg:waitress#main
listen = localhost:6543

[loggers]
keys = root, your_app

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = INFO
handlers = console

[logger_your_app]
level = DEBUG
handlers =
qualname = your_app

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(asctime)s %(levelname)-5.5s [%(name)s:%(lineno)s][%(funcName)s()] %(message)s
```

Then run with:

```bash
pserve development.ini
```

### Integration with Existing Pyramid Apps

If you have an existing Pyramid application, integration is simple:

```python
def main(global_config, **settings):
    config = Configurator(settings=settings)
    
    # Your existing configuration
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    
    # Add pyramid-capstone
    config.include('pyramid_capstone')
    
    # Scan for both regular views and th_api decorated views
    config.scan()
    
    return config.make_wsgi_app()
```

## Next Steps

Now that you have a basic API running, you might want to:

- **[Follow the Tutorial](tutorial.md)** - Learn more advanced features with a complete example
- **[Add Security](security.md)** - Protect your endpoints with authentication
- **[See Examples](examples.md)** - Explore real-world patterns and use cases

## Common Issues

### Import Errors

If you get import errors, make sure you have all dependencies installed:

```bash
poetry add pyramid cornice marshmallow
```

Or with pip:

```bash
pip install pyramid cornice marshmallow
```

### Scanning Issues

If your decorated functions aren't being found, make sure:

1. You're calling `config.scan()` after including the library
2. Your decorated functions are in modules that get imported
3. You're not defining functions inside other functions

### Type Validation Errors

If you're getting unexpected validation errors:

1. Check that your type hints match the expected data types
2. Remember that URL path parameters are always strings initially
3. JSON numbers become `int` or `float` based on your type hints

Need help? Check out our [examples](examples.md) or open an issue on GitHub!
