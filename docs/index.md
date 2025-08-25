# pyramid-capstone

[![Release](https://img.shields.io/github/v/release/tomascorrea/pyramid-capstone)](https://github.com/tomascorrea/pyramid-capstone/releases)
[![Build status](https://img.shields.io/github/actions/workflow/status/tomascorrea/pyramid-capstone/on-release-main.yml?branch=main)](https://github.com/tomascorrea/pyramid-capstone/actions/workflows/on-release-main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/tomascorrea/pyramid-capstone/branch/main/graph/badge.svg)](https://codecov.io/gh/tomascorrea/pyramid-capstone)
[![License](https://img.shields.io/github/license/tomascorrea/pyramid-capstone)](https://img.shields.io/github/license/tomascorrea/pyramid-capstone)

**FastAPI-like decorators for Pyramid** - Build type-safe REST APIs with automatic validation, serialization, and OpenAPI documentation.

## ✨ What is pyramid-capstone?

`pyramid-capstone` enhances Pyramid's already excellent foundation with modern developer conveniences. Built on Pyramid's proven architecture of robustness, flexibility, and enterprise-grade security, it adds automatic validation, serialization, and documentation generation while preserving Pyramid's minimalist philosophy.

### 🎯 Key Features

- **⚡ Developer Experience**: Modern decorators with automatic validation and serialization
- **🏗️ Pyramid Foundation**: Built on Pyramid's battle-tested, production-ready framework
- **🔗 Seamless Integration**: Works perfectly with existing Pyramid applications and middleware
- **📚 Auto Documentation**: Automatic OpenAPI/Swagger documentation generation
- **🛡️ Enterprise Security**: Leverages Pyramid's comprehensive security and authentication system
- **🧪 Production Ready**: Comprehensive test suite built on Pyramid's reliability

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

## 🏃‍♂️ Getting Started

Ready to start building type-safe APIs? Check out our [Getting Started Guide](getting-started.md) for installation instructions and your first API endpoint.

## 📚 Documentation

- **[Getting Started](getting-started.md)** - Installation and basic setup
- **[Tutorial](tutorial.md)** - Step-by-step guide with examples
- **[Security](security.md)** - Authentication and authorization
- **[API Reference](modules.md)** - Complete API documentation
- **[Examples](examples.md)** - Real-world examples and patterns

## 🎯 Why Choose pyramid-capstone?

pyramid-capstone combines Pyramid's enterprise-grade foundation with modern developer experience:

| Feature | pyramid-capstone | Pure Pyramid | Pure Cornice |
|---------|------------------------|---------------|--------------|
| **Developer Experience** | ✅ Modern + Simple | ✅ Minimal | ⚠️ Schema-heavy |
| **Auto Validation** | ✅ Type-hint based | ❌ Manual setup | ✅ Schema-based |
| **OpenAPI Docs** | ✅ Auto-generated | ❌ Manual | ⚠️ Limited |
| **Production Readiness** | ✅ Pyramid foundation | ✅ Battle-tested | ✅ Pyramid foundation |
| **Security & Auth** | ✅ Full Pyramid power | ✅ Comprehensive | ✅ Full Pyramid power |
| **Flexibility** | ✅ Pyramid's strength | ✅ Maximum | ✅ Pyramid's strength |
| **Learning Curve** | ✅ Gentle enhancement | ⚠️ Framework mastery | ⚠️ Schema complexity |

**The Best of Both Worlds**: Get Pyramid's proven robustness, security, and flexibility with the convenience of automatic validation and documentation.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/tomascorrea/pyramid-capstone/blob/main/CONTRIBUTING.rst) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/tomascorrea/pyramid-capstone/blob/main/LICENSE) file for details.