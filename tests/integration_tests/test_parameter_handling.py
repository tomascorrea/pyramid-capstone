"""
Integration tests for parameter handling.

Tests path parameters, query parameters, and JSON body parameters.
"""
from dataclasses import dataclass
from typing import Optional

from pyramid_capstone import th_api


@dataclass
class CreateUserRequest:
    """Request model for creating users."""

    name: str
    email: str
    age: Optional[int] = None


@dataclass
class UserResponse:
    """Response model for user operations."""

    id: int
    name: str
    email: str
    age: Optional[int] = None
    created: bool = False


@th_api.get("/search")
def search_items(request, query: str, limit: int = 10, offset: int = 0) -> dict:
    """Search with query parameters."""
    return {
        "query": query,
        "limit": limit,
        "offset": offset,
        "results": [f"result-{i}" for i in range(offset, offset + min(limit, 3))],
    }


@th_api.get("/item/{item_id}/details")
def get_item_details(request, item_id: int, include_metadata: bool = False) -> dict:
    """Get item details with path and query parameters."""
    result = {"item_id": item_id, "name": f"Item {item_id}", "status": "active"}

    if include_metadata:
        result["metadata"] = {"created_at": "2024-01-01", "updated_at": "2024-01-02"}

    return result


@th_api.post("/users/create")
def create_user(request, name: str, email: str, age: Optional[int] = None) -> UserResponse:
    """Create user with JSON body parameters."""
    return UserResponse(id=999, name=name, email=email, age=age, created=True)  # Mock ID


@th_api.put("/users/{user_id}/update")
def update_user(request, user_id: int, name: str, email: str, age: Optional[int] = None) -> UserResponse:
    """Update user with path and body parameters."""
    return UserResponse(id=user_id, name=name, email=email, age=age, created=False)


def test_query_parameters(app_factory):
    """Test endpoint with query parameters."""
    app = app_factory(scan_packages=[__name__])

    response = app.get("/search?query=python&limit=5&offset=2")

    assert response.status_code == 200
    data = response.json
    assert data["query"] == "python"
    assert data["limit"] == 5
    assert data["offset"] == 2
    assert len(data["results"]) == 3  # Limited by mock data


def test_query_parameters_with_defaults(app_factory):
    """Test query parameters with default values."""
    app = app_factory(scan_packages=[__name__])

    response = app.get("/search?query=test")

    assert response.status_code == 200
    data = response.json
    assert data["query"] == "test"
    assert data["limit"] == 10  # Default value
    assert data["offset"] == 0  # Default value


def test_path_and_query_parameters(app_factory):
    """Test endpoint with both path and query parameters."""
    app = app_factory(scan_packages=[__name__])

    response = app.get("/item/42/details?include_metadata=true")

    assert response.status_code == 200
    data = response.json
    assert data["item_id"] == 42
    assert data["name"] == "Item 42"
    assert data["status"] == "active"
    assert "metadata" in data
    assert data["metadata"]["created_at"] == "2024-01-01"


def test_path_and_query_parameters_without_optional(app_factory):
    """Test path and query parameters without optional parameter."""
    app = app_factory(scan_packages=[__name__])

    response = app.get("/item/123/details")

    assert response.status_code == 200
    data = response.json
    assert data["item_id"] == 123
    assert data["name"] == "Item 123"
    assert data["status"] == "active"
    assert "metadata" not in data


def test_json_body_parameters(app_factory):
    """Test endpoint with JSON body parameters."""
    app = app_factory(scan_packages=[__name__])

    user_data = {"name": "John Doe", "email": "john@example.com", "age": 30}

    response = app.post_json("/users/create", user_data)

    assert response.status_code == 200
    data = response.json
    assert data["id"] == 999
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert data["age"] == 30
    assert data["created"] is True


def test_json_body_parameters_with_optional(app_factory):
    """Test JSON body parameters with optional field omitted."""
    app = app_factory(scan_packages=[__name__])

    user_data = {
        "name": "Jane Smith",
        "email": "jane@example.com"
        # age omitted (optional)
    }

    response = app.post_json("/users/create", user_data)

    assert response.status_code == 200
    data = response.json
    assert data["name"] == "Jane Smith"
    assert data["email"] == "jane@example.com"
    assert data["age"] is None
    assert data["created"] is True


def test_path_and_body_parameters(app_factory):
    """Test endpoint with both path and body parameters."""
    app = app_factory(scan_packages=[__name__])

    user_data = {"name": "Updated User", "email": "updated@example.com", "age": 25}

    response = app.put_json("/users/456/update", user_data)

    assert response.status_code == 200
    data = response.json
    assert data["id"] == 456  # From path
    assert data["name"] == "Updated User"  # From body
    assert data["email"] == "updated@example.com"  # From body
    assert data["age"] == 25  # From body
    assert data["created"] is False  # Update, not create


def test_parameter_type_conversion(app_factory):
    """Test that parameters are properly converted to correct types."""
    app = app_factory(scan_packages=[__name__])

    # Test integer and boolean conversion from query strings
    response = app.get("/item/789/details?include_metadata=false")

    assert response.status_code == 200
    data = response.json
    assert data["item_id"] == 789  # String "789" converted to int
    assert isinstance(data["item_id"], int)
    # include_metadata=false should result in no metadata
