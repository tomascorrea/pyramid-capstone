# pyramid-type-hinted-api

[![Release](https://img.shields.io/github/v/release/tomas_correa/pyramid-type-hinted-api)](https://img.shields.io/github/v/release/tomas_correa/pyramid-type-hinted-api)
[![Build status](https://img.shields.io/github/actions/workflow/status/tomas_correa/pyramid-type-hinted-api/main.yml?branch=main)](https://github.com/tomas_correa/pyramid-type-hinted-api/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/tomas_correa/pyramid-type-hinted-api/branch/main/graph/badge.svg)](https://codecov.io/gh/tomas_correa/pyramid-type-hinted-api)
[![Commit activity](https://img.shields.io/github/commit-activity/m/tomas_correa/pyramid-type-hinted-api)](https://img.shields.io/github/commit-activity/m/tomas_correa/pyramid-type-hinted-api)
[![License](https://img.shields.io/github/license/tomas_correa/pyramid-type-hinted-api)](https://img.shields.io/github/license/tomas_correa/pyramid-type-hinted-api)

**FastAPI-like decorators for Pyramid** - Build type-safe REST APIs with automatic validation, serialization, and OpenAPI documentation.

- **📖 Documentation**: <https://tomas_correa.github.io/pyramid-type-hinted-api/>
- **🔧 Source Code**: <https://github.com/tomas_correa/pyramid-type-hinted-api/>
- **🐍 PyPI**: <https://pypi.org/project/pyramid-type-hinted-api/>

## ✨ What is pyramid-type-hinted-api?

`pyramid-type-hinted-api` brings the developer experience of FastAPI to the Pyramid web framework. Write clean, type-safe API endpoints with automatic request validation, response serialization, and OpenAPI documentation generation.

### 🎯 Key Features

- **🔒 Type Safety**: Full type hint support with automatic validation
- **⚡ Zero Boilerplate**: Minimal code, maximum functionality
- **🔗 Pyramid Integration**: Works seamlessly with existing Pyramid applications
- **📚 Auto Documentation**: Automatic OpenAPI/Swagger documentation
- **🛡️ Security Ready**: Built-in support for Pyramid's security system
- **🧪 Battle Tested**: Comprehensive test suite with 95%+ coverage

### 🚀 Quick Example

```python
from pyramid_type_hinted_api import th_api

@th_api.get('/users/{user_id}')
def get_user(request, user_id: int) -> dict:
    return {"id": user_id, "name": "John Doe"}

@th_api.post('/users')
def create_user(request, name: str, email: str) -> dict:
    # Parameters automatically extracted and validated from JSON body
    return {"message": "User created", "name": name, "email": email}
```

That's it! No manual schema definitions, no boilerplate validation code.

## 🏃‍♂️ Quick Start

### Installation

```bash
pip install pyramid-type-hinted-api
```

### Basic Setup

```python
from pyramid.config import Configurator
from pyramid_type_hinted_api import th_api

# Include the library in your Pyramid app
def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_type_hinted_api')
    
    # Scan for your decorated views
    config.scan()
    
    return config.make_wsgi_app()
```

## 🎯 Why Choose pyramid-type-hinted-api?

| Feature | pyramid-type-hinted-api | Pure Pyramid | Pure Cornice |
|---------|------------------------|---------------|--------------|
| Type Safety | ✅ Built-in | ❌ Manual | ❌ Manual |
| Auto Validation | ✅ Automatic | ❌ Manual | ⚠️ Schema required |
| OpenAPI Docs | ✅ Generated | ❌ Manual | ⚠️ Limited |
| Boilerplate | ✅ Minimal | ❌ Verbose | ⚠️ Medium |
| Learning Curve | ✅ Gentle | ⚠️ Steep | ⚠️ Medium |

## 📚 Learn More

- **[📖 Full Documentation](https://tomas_correa.github.io/pyramid-type-hinted-api/)** - Complete guides and API reference
- **[🚀 Getting Started](https://tomas_correa.github.io/pyramid-type-hinted-api/getting-started/)** - Step-by-step tutorial
- **[💡 Examples](examples/blog_api/)** - Complete blog API example with advanced features
- **[🔒 Security Guide](https://tomas_correa.github.io/pyramid-type-hinted-api/security/)** - Authentication and authorization

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.rst) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.