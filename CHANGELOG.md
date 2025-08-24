# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-19

### 🎉 Initial Release

This is the first public release of **pyramid-capstone** (formerly pyramid-type-hinted-api), a FastAPI-like decorator system for the Pyramid web framework.

**⚠️ Development Status**: This is an early development release (v0.1.x) and should NOT be used in production environments. The API may change significantly between versions until we reach v1.0.0.

### ✨ Features

#### Core Functionality
- **Type-hinted API decorators**: Write clean, type-safe endpoints with `@th_api.get()`, `@th_api.post()`, etc.
- **Automatic validation**: Request parameters are automatically validated based on type hints
- **Automatic serialization**: Response objects are automatically serialized to JSON
- **Parameter injection**: Pytest-style dependency injection for request parameters
- **Multiple parameter sources**: Support for path parameters, query parameters, and JSON body
- **Type conversion**: Automatic conversion between string inputs and Python types

#### HTTP Methods Support
- `@th_api.get()` - GET requests
- `@th_api.post()` - POST requests  
- `@th_api.put()` - PUT requests
- `@th_api.patch()` - PATCH requests
- `@th_api.delete()` - DELETE requests
- `@th_api.options()` - OPTIONS requests
- `@th_api.head()` - HEAD requests

#### Advanced Features
- **Security integration**: Built-in support for Pyramid's authentication/authorization system
- **Complex types**: Support for `List`, `Optional`, `Union`, and custom dataclasses
- **Error handling**: Comprehensive error handling with proper HTTP status codes
- **OpenAPI documentation**: Automatic OpenAPI/Swagger documentation generation (via pycornmarsh)
- **Cornice integration**: Built on top of Cornice for robust service handling

### 📚 Documentation

- **Comprehensive guides**: Getting started, tutorial, security, and API reference
- **Real-world examples**: Complete blog API example with CRUD operations
- **MkDocs integration**: Beautiful documentation with Material theme
- **Code examples**: Extensive examples for all features

### 🧪 Testing

- **216 test cases**: Comprehensive test suite with high coverage
- **Integration tests**: Real-world scenario testing
- **Unit tests**: Individual component testing
- **Example tests**: Validation of all example code

### 🏗️ Infrastructure

- **Poetry**: Modern Python dependency management
- **GitHub Actions**: Automated CI/CD pipeline
- **Pre-commit hooks**: Code quality enforcement
- **Multiple Python versions**: Support for Python 3.9, 3.10, 3.11, 3.12
- **Code quality tools**: Black, Ruff, pytest, coverage

### 📦 Installation

```bash
pip install pyramid-capstone
```

### 🚀 Quick Start

```python
from pyramid.config import Configurator
from pyramid_capstone import th_api

@th_api.get('/users/{user_id}')
def get_user(request, user_id: int) -> dict:
    return {"id": user_id, "name": "John Doe"}

@th_api.post('/users')
def create_user(request, name: str, email: str) -> dict:
    return {"message": "User created", "name": name, "email": email}

# Pyramid app setup
def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_capstone')
    config.scan()
    return config.make_wsgi_app()
```

### 🔗 Links

- **Documentation**: https://tomas_correa.github.io/pyramid-capstone/
- **Source Code**: https://github.com/tomas_correa/pyramid-capstone/
- **PyPI**: https://pypi.org/project/pyramid-capstone/

### 🙏 Acknowledgments

This project brings the developer experience of FastAPI to the Pyramid ecosystem, making it easy to build type-safe REST APIs with minimal boilerplate.

---

## [Unreleased]

### Added
- Nothing yet

### Changed
- Nothing yet

### Deprecated
- Nothing yet

### Removed
- Nothing yet

### Fixed
- Nothing yet

### Security
- Nothing yet
