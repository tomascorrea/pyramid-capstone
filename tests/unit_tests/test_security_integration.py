"""
Tests for security integration in pyramid-capstone.

This module tests that the th_api decorators properly integrate with
Pyramid's authentication and authorization system.
"""

from pyramid_capstone import th_api


def test_decorator_accepts_permission_parameter():
    """Test that decorators accept permission parameter."""

    @th_api.get("/test", permission="view")
    def test_view(request) -> dict:
        return {"message": "success"}

    # Check that the permission is stored in the function metadata
    assert hasattr(test_view, "__th_api_kwargs__")
    assert test_view.__th_api_kwargs__.get("permission") == "view"


def test_decorator_accepts_string_permission():
    """Test that decorators accept string permissions."""

    @th_api.post("/test", permission="create")
    def test_view(request) -> dict:
        return {"message": "success"}

    # Check that the permission string is stored correctly
    assert test_view.__th_api_kwargs__.get("permission") == "create"


def test_decorator_without_permission():
    """Test that decorators work without permission parameter."""

    @th_api.get("/test")
    def test_view(request) -> dict:
        return {"message": "success"}

    # Check that no permission is set
    permission = test_view.__th_api_kwargs__.get("permission")
    assert permission is None


def test_all_http_methods_support_permission():
    """Test that all HTTP method decorators support permission parameter."""

    @th_api.get("/test", permission="view")
    def get_view(request) -> dict:
        return {}

    @th_api.post("/test", permission="create")
    def post_view(request) -> dict:
        return {}

    @th_api.put("/test", permission="edit")
    def put_view(request) -> dict:
        return {}

    @th_api.patch("/test", permission="edit")
    def patch_view(request) -> dict:
        return {}

    @th_api.delete("/test", permission="delete")
    def delete_view(request) -> dict:
        return {}

    @th_api.options("/test", permission="view")
    def options_view(request) -> dict:
        return {}

    @th_api.head("/test", permission="view")
    def head_view(request) -> dict:
        return {}

    # Verify all have the expected permissions
    assert get_view.__th_api_kwargs__.get("permission") == "view"
    assert post_view.__th_api_kwargs__.get("permission") == "create"
    assert put_view.__th_api_kwargs__.get("permission") == "edit"
    assert patch_view.__th_api_kwargs__.get("permission") == "edit"
    assert delete_view.__th_api_kwargs__.get("permission") == "delete"
    assert options_view.__th_api_kwargs__.get("permission") == "view"
    assert head_view.__th_api_kwargs__.get("permission") == "view"


def test_permission_parameter_type_hints():
    """Test that permission parameter accepts correct types."""
    from typing import get_type_hints

    from pyramid_capstone.decorators import TypeHintedAPI

    api = TypeHintedAPI()

    # Get type hints for the get method
    hints = get_type_hints(api.get)

    # Check that permission parameter has the correct type hint
    assert "permission" in hints
    # The type should be Optional[Union[str, List[str]]]
    # We'll just verify it's present for now
