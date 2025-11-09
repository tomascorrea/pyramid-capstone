"""
Tests for pycornmarsh OpenAPI documentation integration.

This module tests that pyramid_capstone properly integrates with pycornmarsh
to generate OpenAPI documentation automatically.
"""

import pytest


def test_api_explorer_endpoint_exists(test_blog_app):
    """Test that the API explorer endpoint is accessible."""
    # pyramid-capstone sets up /api/{version}/api-explorer
    response = test_blog_app.get("/api/v1/api-explorer")
    assert response.status_code == 200


def test_openapi_spec_endpoint_exists(test_blog_app):
    """Test that the OpenAPI spec endpoint is accessible."""
    # pyramid-capstone sets up /api/{version}/openapi.json
    response = test_blog_app.get("/api/v1/openapi.json")
    assert response.status_code == 200


def test_openapi_json_structure(test_blog_app):
    """Test that OpenAPI JSON has valid structure."""
    response = test_blog_app.get("/api/v1/openapi.json")
    assert response.status_code == 200
    
    data = response.json
    
    # Validate basic OpenAPI structure
    assert "openapi" in data, "OpenAPI spec should have 'openapi' version field"
    assert "info" in data, "OpenAPI spec should have 'info' field"
    assert "paths" in data, "OpenAPI spec should have 'paths' field"
    
    # Check OpenAPI version
    assert data["openapi"].startswith("3."), f"Expected OpenAPI 3.x, got {data['openapi']}"
    
    # Check info section
    assert "title" in data["info"], "OpenAPI info should have 'title'"
    assert "version" in data["info"], "OpenAPI info should have 'version'"


def test_openapi_json_includes_endpoints(test_blog_app):
    """Test that OpenAPI JSON includes our API endpoints."""
    response = test_blog_app.get("/api/v1/openapi.json")
    assert response.status_code == 200
    
    data = response.json
    paths = data.get("paths", {})
    
    # We should have at least some paths documented
    assert len(paths) > 0, "OpenAPI spec should document at least some API paths"


def test_openapi_json_has_schemas(test_blog_app):
    """Test that OpenAPI JSON includes schema definitions."""
    response = test_blog_app.get("/api/v1/openapi.json")
    assert response.status_code == 200
    
    data = response.json
    
    # Check for components section with schemas
    assert "components" in data, "OpenAPI spec should have 'components' section"
    schemas = data["components"].get("schemas", {})
    assert len(schemas) > 0, "OpenAPI spec should include schema definitions from Marshmallow models"

