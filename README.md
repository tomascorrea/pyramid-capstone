# pyramid-capstone

[![Release](https://img.shields.io/github/v/release/tomas_correa/pyramid-capstone)](https://img.shields.io/github/v/release/tomas_correa/pyramid-capstone)
[![Build status](https://img.shields.io/github/actions/workflow/status/tomas_correa/pyramid-capstone/main.yml?branch=main)](https://github.com/tomas_correa/pyramid-capstone/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/tomas_correa/pyramid-capstone/branch/main/graph/badge.svg)](https://codecov.io/gh/tomas_correa/pyramid-capstone)
[![Commit activity](https://img.shields.io/github/commit-activity/m/tomas_correa/pyramid-capstone)](https://img.shields.io/github/commit-activity/m/tomas_correa/pyramid-capstone)
[![License](https://img.shields.io/github/license/tomas_correa/pyramid-capstone)](https://img.shields.io/github/license/tomas_correa/pyramid-capstone)

**FastAPI-like decorators for Pyramid** - Build type-safe REST APIs with automatic validation, serialization, and OpenAPI documentation.

> **⚠️ Development Status Warning**
> 
> **This project is in early development (v0.1.x) and should NOT be used in production environments.**
> 
> While we have comprehensive tests and the core functionality works, the API may change significantly between versions. Use at your own risk and expect breaking changes until we reach v1.0.0.

- **📖 Documentation**: <https://tomas_correa.github.io/pyramid-capstone/>
- **🔧 Source Code**: <https://github.com/tomas_correa/pyramid-capstone/>
- **🐍 PyPI**: <https://pypi.org/project/pyramid-capstone/

## ✨ What is pyramid-capstone?

`pyramid-capstone` brings the developer experience of FastAPI to the Pyramid web framework. Write clean, type-safe API endpoints with automatic request validation, response serialization, and OpenAPI documentation generation.

### 🎯 Key Features

- **🔒 Type Safety**: Full type hint support with automatic validation
- **⚡ Zero Boilerplate**: Minimal code, maximum functionality
- **🔗 Pyramid Integration**: Works seamlessly with existing Pyramid applications
- **📚 Auto Documentation**: Automatic OpenAPI/Swagger documentation
- **🛡️ Security Ready**: Built-in support for Pyramid's security system
- **🧪 Well Tested**: Comprehensive test suite with high coverage

### 🚀 Quick Example

```python
from pyramid.config import Configurator
from pyramid_capstone import th_api

@th_api.get('/users/{user_id}')
def get_user(request, user_id: int) -> dict:
    return {"id": user_id, "name": "John Doe"}

@th_api.post('/users')
def create_user(request, name: str, email: str) -> dict:
    # Parameters automatically extracted and validated from JSON body
    return {"message": "User created", "name": name, "email": email}

# Pyramid app setup
def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_capstone')
    config.scan()
    return config.make_wsgi_app()
```

That's it! No manual schema definitions, no boilerplate validation code.

## 🏃‍♂️ Quick Start

### Installation

```bash
pip install pyramid-capstone
```

### Basic Setup

```python
from pyramid.config import Configurator
from pyramid_capstone import th_api

# Include the library in your Pyramid app
def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_capstone')
    
    # Scan for your decorated views
    config.scan()
    
    return config.make_wsgi_app()
```

## 🎯 Why Choose pyramid-capstone?

| Feature | pyramid-capstone | Pure Pyramid | Pure Cornice |
|---------|------------------------|---------------|--------------|
| Type Safety | ✅ Built-in | ❌ Manual | ❌ Manual |
| Auto Validation | ✅ Automatic | ❌ Manual | ⚠️ Schema required |
| OpenAPI Docs | ✅ Generated | ❌ Manual | ⚠️ Limited |
| Boilerplate | ✅ Minimal | ❌ Verbose | ⚠️ Medium |
| Learning Curve | ✅ Gentle | ⚠️ Steep | ⚠️ Medium |

## 📚 Learn More

- **[📖 Full Documentation](https://tomas_correa.github.io/pyramid-capstone/)** - Complete guides and API reference
- **[🚀 Getting Started](https://tomas_correa.github.io/pyramid-capstone/getting-started/)** - Step-by-step tutorial
- **[💡 Examples](examples/blog_api/)** - Complete blog API example with advanced features
- **[🔒 Security Guide](https://tomas_correa.github.io/pyramid-capstone/security/)** - Authentication and authorization

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.rst) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.