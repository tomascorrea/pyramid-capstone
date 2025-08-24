# Current Active Tasks

This file tracks the tasks currently being worked on (max 1-3 task groups).

## Phase 6: Example Applications & Documentation

### Current Focus: Example Applications

#### Task Group 1: Blog API Example Application
**Status**: COMPLETED
**Priority**: High
**Description**: Create a comprehensive example application demonstrating real-world usage of pyramid-type-hinted-api

**Subtasks**:
- [x] Design the example application structure
  - [x] Blog posts with CRUD operations
  - [x] User management (authors)
  - [x] Comments system
  - [x] Categories/tags
- [x] Create example application directory structure
  - [x] `examples/blog_api/` directory
  - [x] Proper Pyramid application setup with pserve
  - [x] Configuration files (development.ini)
- [x] Implement core models and endpoints
  - [x] User model and endpoints (`/users/`)
  - [x] Post model and endpoints (`/posts/`)
  - [x] Comment model and endpoints (`/comments/`)
  - [x] Category model and endpoints (`/categories/`)
- [x] Demonstrate advanced features
  - [x] Complex return types (nested objects, lists)
  - [x] Parameter validation and error handling
  - [x] Query parameters (pagination, filtering, sorting)
  - [x] Optional fields and default values
- [x] Add OpenAPI documentation integration
  - [x] Integrated pycornmarsh for automatic OpenAPI generation
  - [x] Swagger UI available at `/swagger-ui/`
  - [x] ReDoc available at `/redoc/`
  - [x] OpenAPI JSON at `/openapi.json`
- [x] Add example application documentation
  - [x] README with setup instructions
  - [x] API documentation links
  - [x] Usage examples

**Acceptance Criteria**:
- [x] Complete working Pyramid application using th_api decorators
- [x] Demonstrates all major features of the library
- [x] Easy to run and explore (`pserve development.ini`)
- [x] Well-documented with clear examples
- [x] Shows real-world patterns and best practices
- [x] Automatic OpenAPI documentation with Swagger UI
- [x] Includes comprehensive sample data and realistic API patterns

**Estimated Effort**: 2-3 hours
**Dependencies**: None (all core functionality is complete)

---

## Phase 7: Security Integration

### Current Focus: Pyramid Security Integration

#### Task Group 1: Security Support in th_api Decorators
**Status**: COMPLETED
**Priority**: High
**Description**: Integrate Pyramid's authentication/authorization system into th_api decorators

**Subtasks**:
- [x] Add optional `permission` parameter to all HTTP method decorators
  - [x] Support string permission (e.g., `'view'`)
- [x] Modify service builder to pass permission to Cornice services
- [x] Update view handler creation to integrate with Pyramid's security
- [x] Add unit tests for security integration
- [x] Add integration tests with configured security policies
- [ ] Update documentation with security examples

**Acceptance Criteria**:
- [x] Users can write `@th_api.get('/users', permission='view')`
- [x] Permission parameter is optional (backward compatibility)
- [x] Pyramid handles all security checks and exceptions
- [x] Works with any Pyramid authentication/authorization policy
- [x] Comprehensive test coverage

**Estimated Effort**: 1-2 hours
**Dependencies**: Understanding of Pyramid's security system

---

## Next Up (Backlog)

### Task Group 2: Documentation
- [ ] API reference documentation
- [ ] Tutorial and getting started guide
- [ ] Best practices guide
- [ ] Migration guide from pure Cornice
- [ ] Security integration examples and best practices

### Task Group 3: Performance & Polish
- [ ] Performance benchmarks
- [ ] Error message improvements
- [ ] Edge case handling
- [ ] Optional optimizations
