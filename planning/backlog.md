# Backlog - Future Tasks

This file contains planned future tasks that are not currently being worked on.

## Documentation Tasks

### API Reference Documentation
**Priority**: High
**Description**: Create comprehensive API reference documentation
**Tasks**:
- [ ] Document all public APIs and classes
- [ ] Include code examples for each feature
- [ ] Document configuration options
- [ ] Create troubleshooting guide

### Tutorial and Getting Started Guide
**Priority**: High  
**Description**: Create user-friendly tutorial for new users
**Tasks**:
- [ ] Quick start guide (5-minute setup)
- [ ] Step-by-step tutorial building a simple API
- [ ] Comparison with FastAPI and pure Cornice
- [ ] Common patterns and recipes

### Best Practices Guide
**Priority**: Medium
**Description**: Document recommended patterns and practices
**Tasks**:
- [ ] Path design recommendations
- [ ] Error handling patterns
- [ ] Testing strategies
- [ ] Performance considerations

## Performance & Optimization Tasks

### Performance Benchmarks
**Priority**: Medium
**Description**: Create benchmarks comparing th_api vs hand-written Cornice
**Tasks**:
- [ ] Create benchmark test suite
- [ ] Compare request/response times
- [ ] Memory usage analysis
- [ ] Throughput testing

### Performance Optimizations
**Priority**: Low
**Description**: Optimize hot paths and reduce overhead
**Tasks**:
- [ ] Profile schema generation performance
- [ ] Cache generated schemas when possible
- [ ] Optimize parameter extraction
- [ ] Reduce import overhead

## Advanced Features (Future)

### Enhanced Type Support
**Priority**: Low
**Description**: Support for more complex type scenarios
**Tasks**:
- [ ] Nested dataclass validation
- [ ] Custom type converters
- [ ] Union type handling improvements
- [ ] Generic type support

### Authentication & Authorization
**Priority**: Low
**Description**: Built-in patterns for auth beyond the current `permission` parameter
**Tasks**:
- [ ] JWT token validation decorators
- [ ] User context injection

> **Note**: Basic permission support (`@api.get('/path', permission='view')`) was completed in Phase 7. OpenAPI integration via pycornmarsh was completed in Phase 12. See `knowledge/security.md` and `knowledge/openapi.md`.

## Testing Enhancements

### Advanced Test Scenarios
**Priority**: Medium
**Description**: More comprehensive test coverage
**Tasks**:
- [ ] Error handling edge cases
- [ ] Complex nested object validation
- [ ] Large payload testing
- [ ] Concurrent request testing

### Test Utilities
**Priority**: Low
**Description**: Helper utilities for testing th_api applications
**Tasks**:
- [ ] Test client helpers
- [ ] Mock data generators
- [ ] Assertion helpers for API testing
