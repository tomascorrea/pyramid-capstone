"""
Tests for the decorator system.

This module tests the th_api decorators and their integration with venusian.
"""

import pytest
from typing import Dict, Any
from pyramid_capstone import th_api
from pyramid_capstone.decorators import TypeHintedAPI


def test_api_instance_creation():
    """Test that TypeHintedAPI can be instantiated."""
    api = TypeHintedAPI()
    assert api is not None
    assert hasattr(api, 'venusian')


def test_http_method_decorators_exist():
    """Test that all HTTP method decorators are available."""
    api = TypeHintedAPI()
    
    # Test that all expected methods exist
    expected_methods = ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']
    for method in expected_methods:
        assert hasattr(api, method)
        assert callable(getattr(api, method))


def test_decorator_adds_metadata():
    """Test that decorators add the correct metadata to functions."""
    @th_api.get('/test')
    def test_view(request):
        return {'message': 'test'}
    
    # Check that metadata was added
    assert hasattr(test_view, '__th_api_method__')
    assert hasattr(test_view, '__th_api_path__')
    assert hasattr(test_view, '__th_api_kwargs__')
    
    assert test_view.__th_api_method__ == 'GET'
    assert test_view.__th_api_path__ == '/test'
    assert test_view.__th_api_kwargs__ == {'permission': None}


def test_decorator_with_kwargs():
    """Test that decorators handle additional keyword arguments."""
    @th_api.post('/users', description='Create a user')
    def create_user(request, name: str):
        return {'name': name}
    
    assert create_user.__th_api_method__ == 'POST'
    assert create_user.__th_api_path__ == '/users'
    assert create_user.__th_api_kwargs__ == {'description': 'Create a user', 'permission': None}


def test_venusian_attachment():
    """Test that venusian callback is attached to decorated functions."""
    @th_api.get('/venusian-test')
    def venusian_test_view(request):
        return {}
    
    # Check that venusian has attached metadata
    assert hasattr(venusian_test_view, '__venusian_callbacks__')
    
    callbacks = venusian_test_view.__venusian_callbacks__
    assert callbacks is not None
    
    # Check that our callback is in the right category
    # Venusian callbacks are stored as a dict, not a list
    assert 'pyramid_type_hinted' in callbacks


def test_get_decorator():
    """Test the GET decorator."""
    @th_api.get('/users/{user_id}')
    def get_user(request, user_id: int):
        return {'user_id': user_id}
    
    assert get_user.__th_api_method__ == 'GET'
    assert get_user.__th_api_path__ == '/users/{user_id}'


def test_post_decorator():
    """Test the POST decorator."""
    @th_api.post('/users')
    def create_user(request, name: str, email: str):
        return {'name': name, 'email': email}
    
    assert create_user.__th_api_method__ == 'POST'
    assert create_user.__th_api_path__ == '/users'


def test_put_decorator():
    """Test the PUT decorator."""
    @th_api.put('/users/{user_id}')
    def update_user(request, user_id: int, name: str):
        return {'user_id': user_id, 'name': name}
    
    assert update_user.__th_api_method__ == 'PUT'
    assert update_user.__th_api_path__ == '/users/{user_id}'


def test_patch_decorator():
    """Test the PATCH decorator."""
    @th_api.patch('/users/{user_id}')
    def patch_user(request, user_id: int, name: str = None):
        return {'user_id': user_id, 'name': name}
    
    assert patch_user.__th_api_method__ == 'PATCH'
    assert patch_user.__th_api_path__ == '/users/{user_id}'


def test_delete_decorator():
    """Test the DELETE decorator."""
    @th_api.delete('/users/{user_id}')
    def delete_user(request, user_id: int):
        return {'deleted': user_id}
    
    assert delete_user.__th_api_method__ == 'DELETE'
    assert delete_user.__th_api_path__ == '/users/{user_id}'


def test_options_decorator():
    """Test the OPTIONS decorator."""
    @th_api.options('/users')
    def options_users(request):
        return {}
    
    assert options_users.__th_api_method__ == 'OPTIONS'
    assert options_users.__th_api_path__ == '/users'


def test_head_decorator():
    """Test the HEAD decorator."""
    @th_api.head('/users/{user_id}')
    def head_user(request, user_id: int):
        return None
    
    assert head_user.__th_api_method__ == 'HEAD'
    assert head_user.__th_api_path__ == '/users/{user_id}'


def test_function_with_type_hints():
    """Test that decorators work with type-hinted functions."""
    @th_api.get('/typed/{item_id}')
    def get_typed_item(request, item_id: int, include_details: bool = False) -> Dict[str, Any]:
        return {
            'item_id': item_id,
            'include_details': include_details,
            'type': 'item'
        }
    
    # Function should retain its annotations
    annotations = get_typed_item.__annotations__
    assert 'item_id' in annotations
    assert annotations['item_id'] is int
    assert 'include_details' in annotations
    assert annotations['include_details'] is bool
    assert annotations['return'] == Dict[str, Any]
    
    # Should also have th_api metadata
    assert get_typed_item.__th_api_method__ == 'GET'
    assert get_typed_item.__th_api_path__ == '/typed/{item_id}'


def test_function_preserves_metadata():
    """Test that decorators preserve function metadata."""
    @th_api.post('/preserve-test')
    def test_function_with_metadata(request, data: str):
        """This is a test function with a docstring."""
        return {'data': data}
    
    # Original function metadata should be preserved
    assert test_function_with_metadata.__name__ == 'test_function_with_metadata'
    assert test_function_with_metadata.__doc__ == 'This is a test function with a docstring.'
    
    # th_api metadata should be added
    assert test_function_with_metadata.__th_api_method__ == 'POST'
    assert test_function_with_metadata.__th_api_path__ == '/preserve-test'


def test_multiple_decorators_on_different_functions():
    """Test that multiple functions can be decorated independently."""
    @th_api.get('/first')
    def first_view(request):
        return {'view': 'first'}
    
    @th_api.post('/second')
    def second_view(request, data: str):
        return {'view': 'second', 'data': data}
    
    # Each function should have its own metadata
    assert first_view.__th_api_method__ == 'GET'
    assert first_view.__th_api_path__ == '/first'
    
    assert second_view.__th_api_method__ == 'POST'
    assert second_view.__th_api_path__ == '/second'
    
    # They should not interfere with each other
    assert first_view.__th_api_method__ != second_view.__th_api_method__
    assert first_view.__th_api_path__ != second_view.__th_api_path__


def test_decorator_with_various_path_formats():
    """Test that decorators can handle various path formats."""
    # These should all work without raising exceptions during decoration
    @th_api.get('')
    def empty_path(request):
        return {}
    
    @th_api.get('/')
    def root_path(request):
        return {}
    
    @th_api.get('/complex/{id}/sub/{sub_id}')
    def complex_path(request, id: int, sub_id: str):
        return {'id': id, 'sub_id': sub_id}
    
    # All should have been decorated successfully
    assert empty_path.__th_api_path__ == ''
    assert root_path.__th_api_path__ == '/'
    assert complex_path.__th_api_path__ == '/complex/{id}/sub/{sub_id}'


def test_decorator_preserves_function_callable():
    """Test that decorated functions remain callable."""
    @th_api.get('/callable-test')
    def callable_test(request):
        return {'status': 'ok'}
    
    # Function should still be callable
    assert callable(callable_test)
    
    # Verify the function object is intact
    assert callable_test.__name__ == 'callable_test'
