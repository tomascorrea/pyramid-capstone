# Pyramid Type-Hinted API Implementation Plan

## Overview
Create a FastAPI-like decorator system for Pyramid that automatically handles validation and serialization using Marshmallow schemas and Cornice services, with type hint inspection for automatic schema generation.

## Architecture Goals

### Core Concept
```python
from pyramid_type_hinted_api import th_api

@th_api.post('/users/{user_id}')
def update_user(request, user_id: int, name: str) -> UserResponse:
    # Business logic here
    return UserResponse(id=user_id, name=name)
```

### Key Features
1. **Type Hint Inspection**: Automatically extract parameter and return types
2. **Pytest-style Dependency Injection**: Match function parameters to request context
3. **Automatic Schema Generation**: Create Marshmallow schemas from type hints
4. **Cornice Integration**: Use Cornice services for validation and error handling
5. **Venusian Registration**: Integrate with Pyramid's configuration scanning

## Implementation Components

### 1. Decorator System (`th_api`)
- **Location**: `pyramid_type_hinted_api/decorators.py`
- **HTTP Methods**: `get`, `post`, `put`, `delete`, `patch`, `options`, `head`
- **Venusian Integration**: Use category "pyramid_type_hinted"

```python
class TypeHintedAPI:
    def __init__(self):
        self.venusian = venusian.Scanner()
    
    def get(self, path: str):
        return self._create_decorator('GET', path)
    
    def post(self, path: str):
        return self._create_decorator('POST', path)
    
    # ... other HTTP methods
```

### 2. Type Inspection System
- **Location**: `pyramid_type_hinted_api/inspection.py`
- **Purpose**: Extract type hints from function signatures
- **Features**:
  - Parse function parameters and their types
  - Extract return type annotations
  - Handle complex types (List, Optional, Union)
  - Validate type compatibility with Marshmallow

```python
def inspect_function_signature(func: Callable) -> FunctionSignature:
    """Extract parameter types and return type from function signature."""
    pass

@dataclass
class FunctionSignature:
    parameters: Dict[str, Type]
    return_type: Optional[Type]
    has_request_param: bool
```

### 3. Context System (Pytest-style Injection)
- **Location**: `pyramid_type_hinted_api/context.py`
- **Purpose**: Build parameter context from HTTP request
- **Conflict Detection**: Validate no parameter name conflicts at setup time

```python
class ParameterContext:
    def __init__(self, path_params: Dict, query_params: Dict, body_params: Dict):
        self.validate_no_conflicts()
        self.context = {**path_params, **query_params, **body_params}
    
    def validate_no_conflicts(self):
        """Ensure no parameter name appears in multiple sources."""
        pass
    
    def extract_function_args(self, signature: FunctionSignature) -> Dict:
        """Match function parameters to available context variables."""
        pass
```

### 4. Schema Generation
- **Location**: `pyramid_type_hinted_api/schema_generator.py`
- **Purpose**: Generate Marshmallow schemas from type hints
- **Support**: Basic types (int, str, bool, float), Lists, custom classes

```python
def generate_input_schema(signature: FunctionSignature) -> Type[Schema]:
    """Generate Marshmallow schema for request validation."""
    pass

def generate_output_schema(return_type: Type) -> Type[Schema]:
    """Generate Marshmallow schema for response serialization."""
    pass
```

### 5. Cornice Service Integration
- **Location**: `pyramid_type_hinted_api/service_builder.py`
- **Purpose**: Create Cornice services dynamically
- **Features**: Automatic validation, error handling, response serialization

```python
def create_cornice_service(
    path: str, 
    method: str, 
    input_schema: Type[Schema], 
    output_schema: Type[Schema]
) -> Service:
    """Create a Cornice service with automatic validation."""
    pass
```

### 6. Request Handler
- **Location**: `pyramid_type_hinted_api/handler.py`
- **Purpose**: Bridge between Cornice and original function
- **Process**:
  1. Extract validated data from request
  2. Build parameter context
  3. Call original function with injected parameters
  4. Serialize response using output schema

```python
def create_view_handler(
    original_func: Callable,
    signature: FunctionSignature,
    input_schema: Type[Schema],
    output_schema: Type[Schema]
) -> Callable:
    """Create the actual view handler that Cornice will call."""
    pass
```

## Implementation Phases

### Phase 0: Environment Setup ✅
- [x] Setup Python environment with pyenv and pyenv-virtualenv
  ```bash
  # Create Python environment
  pyenv virtualenv 3.12.8 pyramid-type-hinted-api
  pyenv local pyramid-type-hinted-api
  ```
- [x] Configure Poetry for dependency management
  ```bash
  # Install Poetry in virtual environment
  pip install poetry
  ```
- [x] Setup direnv for local environment variables
  ```bash
  # Create .envrc file for direnv
  eval "$(pyenv init -)"
  eval "$(pyenv virtualenv-init -)"
  pyenv activate pyramid-type-hinted-api
  direnv allow
  ```
- [x] Install project dependencies
  ```bash
  # Install all dependencies including dev dependencies
  poetry install --with dev,docs
  ```
- [x] Verify development environment is working
  ```bash
  # Run tests to verify setup
  pytest tests/
  # Run linting
  mypy pyramid_type_hinted_api/
  ```

### Phase 1: Core Infrastructure ✅
- [x] Add dependencies (pyramid, cornice, marshmallow, venusian)
- [x] Create basic decorator system with venusian integration
- [x] Implement function signature inspection
- [x] Build parameter context system with conflict detection

### Phase 2: Schema Generation ✅
- [x] Implement basic type to Marshmallow field mapping
- [x] Handle complex types (List, Optional)
- [x] Support for custom classes/dataclasses
- [x] Generate input and output schemas

### Phase 3: Cornice Integration ✅
- [x] Create Cornice services dynamically
- [x] Implement request validation
- [x] Build response serialization
- [x] Error handling integration

### Phase 4: Request Handler ✅
- [x] Create view handler that bridges Cornice and original function
- [x] Implement parameter injection
- [x] Handle request/response lifecycle
- [x] Integration testing

### Phase 5: Testing & Documentation ✅
- [x] Comprehensive test suite (103 tests: 25 integration + 78 unit tests)
  - [x] Unit tests for all core modules (decorators, inspection, context, schema generation)
  - [x] Integration tests organized into 4 clean test files:
    - [x] `test_basic_functionality.py` - Core features and path parameters
    - [x] `test_return_types.py` - All return type variations (dict, dataclass, lists)
    - [x] `test_parameter_handling.py` - Parameter injection (path, query, JSON body)
    - [x] `test_crud_operations.py` - Complete CRUD example with proper path design
  - [x] Parametrized tests for better maintainability
  - [x] Mock-free testing with real Pyramid requests
- [ ] Example applications
- [ ] Documentation and usage guides
- [ ] Performance optimization

### Phase 6: Example Applications & Documentation
- [ ] Create example applications demonstrating real-world usage
- [ ] Write comprehensive documentation
- [ ] Performance benchmarks and optimization

## File Structure
```
pyramid_type_hinted_api/
├── __init__.py              # Main exports (th_api instance)
├── decorators.py            # TypeHintedAPI class and HTTP method decorators
├── inspection.py            # Function signature inspection utilities
├── context.py               # Parameter context and injection system
├── schema_generator.py      # Marshmallow schema generation
├── service_builder.py       # Cornice service creation
├── handler.py               # Request handler and view creation
├── exceptions.py            # Custom exceptions for conflicts and errors
└── utils.py                 # Utility functions and helpers
```

## Error Handling Strategy
- **Setup Time Errors**: Parameter conflicts, invalid type hints, missing dependencies
- **Runtime Errors**: Leverage Cornice's built-in validation error handling
- **Custom Exceptions**: Clear error messages for common configuration issues

## Integration Points
- **Pyramid Configuration**: Works with existing `config.scan()` mechanism
- **Cornice Services**: Leverages existing validation and error handling
- **Marshmallow**: Uses standard schema generation and validation
- **Venusian**: Follows Pyramid's decorator registration pattern

## Success Criteria
1. Clean, FastAPI-like syntax for defining APIs
2. Automatic validation without boilerplate
3. Seamless integration with existing Pyramid applications
4. Clear error messages for configuration issues
5. Performance comparable to hand-written Cornice services
6. Comprehensive test coverage
7. Good documentation and examples
