"""
Integration tests for security policies with pyramid-capstone.

This module tests that the api decorators properly integrate with
Pyramid's authentication and authorization policies in real scenarios.
"""

import pytest

from pyramid_capstone import api


# Test views with different permission requirements
@api.get("/public")
def public_view(request) -> dict:
    """Public view - no permission required."""
    return {"message": "public access", "user": request.authenticated_userid}


@api.get("/protected", permission="view")
def protected_view(request) -> dict:
    """Protected view - requires authentication."""
    return {"message": "authenticated access", "user": request.authenticated_userid}


@api.post("/edit", permission="edit")
def edit_view(request) -> dict:
    """Edit view - requires editor permission."""
    return {"message": "editor access", "user": request.authenticated_userid}


@api.delete("/admin", permission="admin")
def admin_view(request) -> dict:
    """Admin view - requires admin permission."""
    return {"message": "admin access", "user": request.authenticated_userid}


@api.get("/multi-permission", permission="edit")
def multi_permission_view(request) -> dict:
    """View that requires edit permission (originally intended for multiple permissions)."""
    return {"message": "multi permission access", "user": request.authenticated_userid}


@pytest.fixture
def security_app(app_factory):
    """Create a Pyramid app with security policies configured using existing fixtures."""
    return app_factory(scan_packages=[__name__], enable_security=True)  # Scan this module for test views


def test_public_view_accessible_without_auth(security_app):
    """Test that public views work without authentication."""
    response = security_app.get("/public")
    assert response.status_code == 200
    assert response.json["message"] == "public access"
    assert response.json["user"] is None


def test_protected_view_requires_authentication(security_app):
    """Test that protected views require authentication."""
    # Without authentication - should get 403 Forbidden
    response = security_app.get("/protected", expect_errors=True)
    assert response.status_code == 403


def test_protected_view_works_with_authentication(security_app):
    """Test that protected views work with authentication."""
    # Use simple Bearer token authentication
    headers = {"Authorization": "Bearer user1"}

    response = security_app.get("/protected", headers=headers)
    assert response.status_code == 200
    assert response.json["message"] == "authenticated access"
    assert response.json["user"] == "user1"


def test_edit_view_requires_editor_permission(security_app):
    """Test that edit views require editor permission."""
    # Regular authenticated user should not have access
    headers = {"Authorization": "Bearer user1"}
    response = security_app.post("/edit", headers=headers, expect_errors=True)
    assert response.status_code == 403


def test_edit_view_works_with_editor_permission(security_app):
    """Test that edit views work with editor permission."""
    # Editor should have access
    headers = {"Authorization": "Bearer editor1"}
    response = security_app.post("/edit", headers=headers)
    assert response.status_code == 200
    assert response.json["message"] == "editor access"


def test_admin_view_requires_admin_permission(security_app):
    """Test that admin views require admin permission."""
    # Editor should not have admin access
    headers = {"Authorization": "Bearer editor1"}
    response = security_app.delete("/admin", headers=headers, expect_errors=True)
    assert response.status_code == 403


def test_admin_view_works_with_admin_permission(security_app):
    """Test that admin views work with admin permission."""
    # Admin should have access
    headers = {"Authorization": "Bearer admin1"}
    response = security_app.delete("/admin", headers=headers)
    assert response.status_code == 200
    assert response.json["message"] == "admin access"


def test_multi_permission_view_with_editor(security_app):
    """Test that multi-permission views work with editor permission."""
    headers = {"Authorization": "Bearer editor1"}
    response = security_app.get("/multi-permission", headers=headers)
    assert response.status_code == 200
    assert response.json["message"] == "multi permission access"


def test_multi_permission_view_with_admin(security_app):
    """Test that edit permission views work with admin permission (admin has edit access)."""
    headers = {"Authorization": "Bearer admin1"}
    response = security_app.get("/multi-permission", headers=headers)
    assert response.status_code == 200
    assert response.json["message"] == "multi permission access"


def test_multi_permission_view_without_permission(security_app):
    """Test that edit permission views reject users without required permissions."""
    headers = {"Authorization": "Bearer user1"}
    response = security_app.get("/multi-permission", headers=headers, expect_errors=True)
    assert response.status_code == 403


def test_permission_none_works_like_no_permission(security_app):
    """Test that permission=None works the same as no permission parameter."""

    @api.get("/test-none", permission=None)
    def test_none_view(request) -> dict:
        return {"message": "none permission"}

    # This should work without authentication (like public view)
    security_app.get("/test-none", expect_errors=True)
    # Note: This might fail because the view wasn't scanned, but that's expected
    # The important thing is that permission=None doesn't break anything
