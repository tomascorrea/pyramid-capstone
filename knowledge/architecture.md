# Architecture

pyramid-capstone provides FastAPI-style decorators for Pyramid that automatically handle request validation and response serialization via Marshmallow schemas and Cornice services, all derived from function type hints.

## Package Structure

```
pyramid_capstone/
├── __init__.py           # Public API: api instance, includeme, capstone_enable_openapi_docs, exceptions
├── decorators.py         # CapstoneAPI class with HTTP method decorators, Venusian integration
├── inspection.py         # Function signature inspection, ParameterInfo and FunctionSignature dataclasses
├── schema_generator.py   # Marshmallow schema generation from type hints
├── context.py            # Parameter extraction from path/query/body with type conversion
├── service_builder.py    # Cornice service creation, view registration, pycornmarsh predicates
├── handler.py            # View handler bridging Cornice and decorated functions, response serialization
└── exceptions.py         # Exception hierarchy: TypeHintedAPIError and subclasses
```

## Core Design Decisions

### Deferred Registration via Venusian

Decorators (`@api.get`, `@api.post`, etc.) only attach metadata to the function. Real service registration happens during `config.scan()` with `categories=["pyramid_type_hinted"]`. This ensures all decorated functions are discovered before services are built, allowing multiple HTTP methods on the same path to share a single Cornice service.

### One Cornice Service per Path

Views are collected in `pending_views[path]` and turned into Cornice services in a config action with `order=-20`. This means `@api.get('/users')` and `@api.post('/users')` produce one service with two methods, matching how Cornice naturally groups operations.

### Marshmallow for Both Validation and Serialization

Input schemas validate request data; output schemas serialize responses. Schemas are generated automatically from type hints at registration time, not at request time. The type mapping covers: `int`, `float`, `str`, `bool`, `bytes`, `datetime`, `date`, `Enum`, `Optional[T]`, `List[T]`, and annotated classes/dataclasses.

### ListSchemaInfo for List Responses

`generate_output_schema` cannot return a plain Marshmallow schema for `List[ComplexType]` because schemas describe single objects. Instead it returns a `ListSchemaInfo(item_schema)` sentinel. The handler and pycornmarsh predicate builder both check `is_list_schema` to handle iteration.

### Parameter Source Precedence

`ParameterContext` resolves parameter values with strict precedence: path > query > JSON body. Conflicts between sources are detected at registration time via `validate_no_conflicts()`, not at request time.

### Error Dict Passthrough in Output Schemas

Generated output schemas override `dump` to pass through dicts whose keys do not match the schema fields. This allows handlers to return error dicts (e.g. `{"error": "not found"}`) without triggering serialization failures.

### Pyramid Security Integration

The optional `permission` parameter on decorators is forwarded to `service.add_view()`. All authentication and authorization enforcement is handled by Pyramid's security system -- the library does not implement its own auth logic.

## Component Relationships

```
@api.get('/path')          decorators.py: stores metadata, venusian.attach()
        │
        ▼
config.scan()              Venusian invokes callback per decorated function
        │
        ▼
register_type_hinted_view  service_builder.py: collects in pending_views[path]
        │
        ▼
_create_service_for_path   service_builder.py: runs during config commit
        │
        ├── inspect_function_signature()       inspection.py
        ├── ParameterContext(path)             context.py
        ├── generate_input_schema()            schema_generator.py
        ├── generate_output_schema()           schema_generator.py
        ├── create_view_handler()              handler.py
        ├── _build_pycornmarsh_predicates()    service_builder.py
        └── config.add_cornice_service()       Cornice integration
```

At request time:
1. Cornice validator loads data into `request.validated`
2. Handler calls the original function with extracted arguments
3. `handle_response()` serializes the return value via the output schema

## Key Learnings / Gotchas

- **`request` must be the first parameter** of every decorated function. It is not injected via type hints -- it is positional.
- **`request.validated` vs `request.validated_data`**: The active code path uses `request.validated` (set by Cornice validators). There is a legacy `add_validation_to_service` function that sets `request.validated_data` but it is unused. `extract_validated_data` checks `validated_data` first, which can be confusing.
- **Input schema location for OpenAPI**: `_build_pycornmarsh_predicates` always puts the input schema under `pcm_request={"body": input_schema}`, even for GET requests where parameters come from query/path. This is a known simplification.
- **Path parameter type conversion happens in two places**: Marshmallow validators do it during validation, and `ParameterContext._convert_parameter_value` does it during argument building. Both paths can be involved depending on whether validators ran.
- **Routing strategy**: Use completely distinct paths to avoid Pyramid/Cornice route conflicts. Do not rely on method-only differentiation for paths that partially overlap.
- **`dict` and `list` are treated as basic types** in `is_basic_type()`, meaning they skip schema generation. Only annotated classes/dataclasses get full schemas.
