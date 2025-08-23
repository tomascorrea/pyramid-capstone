"""
Integration tests for basic th_api functionality.

Tests the core features: simple endpoints, path parameters, and basic serialization.
"""
from dataclasses import dataclass
from pyramid_type_hinted_api import th_api


@dataclass
class User:
    """Simple user model for testing."""
    id: int
    name: str
    email: str


@th_api.get('/health')
def health_check(request) -> dict:
    """Simple health check endpoint."""
    return {'status': 'ok', 'service': 'pyramid-type-hinted-api'}


@th_api.get('/user/{user_id}')
def get_user(request, user_id: int) -> User:
    """Get user by ID with path parameter."""
    return User(
        id=user_id,
        name=f'User {user_id}',
        email=f'user{user_id}@example.com'
    )


@th_api.get('/message/{text}')
def echo_message(request, text: str) -> dict:
    """Echo a text message."""
    return {'message': text, 'length': len(text)}


def test_health_check(app_factory):
    """Test simple endpoint with dict return."""
    app = app_factory(scan_packages=[__name__])
    
    response = app.get('/health')
    
    assert response.status_code == 200
    assert response.json == {'status': 'ok', 'service': 'pyramid-type-hinted-api'}


def test_get_user_with_path_param(app_factory):
    """Test endpoint with path parameter and dataclass return."""
    app = app_factory(scan_packages=[__name__])
    
    response = app.get('/user/42')
    
    assert response.status_code == 200
    data = response.json
    assert data['id'] == 42
    assert data['name'] == 'User 42'
    assert data['email'] == 'user42@example.com'


def test_echo_message_string_param(app_factory):
    """Test endpoint with string path parameter."""
    app = app_factory(scan_packages=[__name__])
    
    response = app.get('/message/hello-world')
    
    assert response.status_code == 200
    data = response.json
    assert data['message'] == 'hello-world'
    assert data['length'] == 11


def test_path_parameter_type_conversion(app_factory):
    """Test that path parameters are properly converted to correct types."""
    app = app_factory(scan_packages=[__name__])
    
    # Test integer conversion
    response = app.get('/user/999')
    
    assert response.status_code == 200
    data = response.json
    assert data['id'] == 999  # Should be converted from string "999" to int 999
    assert isinstance(data['id'], int)
