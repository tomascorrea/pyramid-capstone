# Security Integration

pyramid-capstone integrates with Pyramid's built-in authentication and authorization system by forwarding an optional `permission` parameter from decorators to Cornice service views.

## Design Decisions

### Delegation to Pyramid's Security System

The library does not implement its own auth logic. The `permission` parameter on each HTTP method decorator (`@api.get`, `@api.post`, etc.) is passed directly to `service.add_view(permission=...)`. Pyramid's security policies handle all checking and exception raising (e.g. `HTTPForbidden`).

This keeps the library focused on type-hint-driven validation and serialization while letting users plug in any Pyramid-compatible security policy (cookie, JWT, header-based, etc.).

### Optional and Backward-Compatible

`permission` defaults to `None` on all decorators. Existing code without permissions continues to work unchanged. Adding permissions requires no changes to the handler function signature.

## API Surface

All HTTP method decorators accept `permission`:

```python
@api.get('/users', permission='view')
def list_users(request) -> List[User]: ...

@api.post('/users', permission='create')
def create_user(request, name: str) -> User: ...
```

The flow:
1. `decorators.py`: `permission` is stored in `kwargs` on the decorated function
2. `service_builder.py`: `kwargs.get("permission")` is passed to `service.add_view()`
3. Pyramid's security system enforces the permission before the handler runs

## Key Learnings / Gotchas

- The library does not raise security exceptions itself. If no security policy is configured in the Pyramid app and a permission is specified, Pyramid will raise an error during configuration or silently skip enforcement depending on the version.
- `permission` accepts a single string, not a list. For multi-permission logic, use a custom Pyramid authorization policy.
- Security checks happen before the Cornice validator and handler run, so invalid requests from unauthorized users are rejected early.
