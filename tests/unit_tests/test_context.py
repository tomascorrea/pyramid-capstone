"""
Tests for the parameter context and dependency injection system.

This module tests the pytest-style parameter extraction and injection
from HTTP requests.
"""

import pytest
from typing import Optional
from pyramid_capstone.context import (
    ParameterContext,
    extract_path_parameters_from_pattern,
    validate_path_pattern
)
from pyramid_capstone.inspection import (
    inspect_function_signature,
    ParameterInfo,
    FunctionSignature
)
from pyramid_capstone.exceptions import (
    ParameterConflictError,
    ParameterMissingError
)


def test_parameter_context_creation():
    """Test creating a ParameterContext."""
    context = ParameterContext('/users/{user_id}')
    assert context.path_pattern == '/users/{user_id}'
    assert 'user_id' in context.path_params


def test_extract_path_parameters():
    """Test extracting path parameters from patterns."""
    context = ParameterContext('/users/{user_id}/posts/{post_id}')
    
    expected_params = {'user_id', 'post_id'}
    assert context.path_params == expected_params


def test_extract_path_parameters_no_params():
    """Test path pattern with no parameters."""
    context = ParameterContext('/users')
    assert len(context.path_params) == 0


def test_extract_path_parameters_complex():
    """Test complex path patterns."""
    context = ParameterContext('/api/v1/users/{user_id}/posts/{post_id}/comments/{comment_id}')
    
    expected_params = {'user_id', 'post_id', 'comment_id'}
    assert context.path_params == expected_params


def test_extract_path_parameters_from_request(app_request):
    """Test extracting path parameters from request matchdict."""
    context = ParameterContext('/users/{user_id}')
    
    # Create a real request with path parameters
    request = app_request(
        path='/users/123',
        method='GET'
    )
    # Simulate matchdict that would be set by Pyramid routing
    request.matchdict = {'user_id': '123'}
    
    params = context.extract_request_parameters(request)
    assert params['user_id'] == '123'


def test_extract_query_parameters_from_request(app_request):
    """Test extracting query parameters from request."""
    context = ParameterContext('/users')
    
    # Create a real request with query parameters
    request = app_request(
        path='/users?limit=10&offset=0',
        method='GET'
    )
    
    params = context.extract_request_parameters(request)
    assert params['limit'] == '10'
    assert params['offset'] == '0'


def test_extract_json_body_parameters(app_request):
    """Test extracting parameters from JSON body."""
    context = ParameterContext('/users')
    
    # Create a real request with JSON body
    request = app_request(
        path='/users',
        method='POST',
        json={'name': 'John', 'email': 'john@example.com'}
    )
    
    params = context.extract_request_parameters(request)
    assert params['name'] == 'John'
    assert params['email'] == 'john@example.com'


def test_parameter_precedence(app_request):
    """Test that path parameters take precedence over query and body."""
    context = ParameterContext('/users/{user_id}')
    
    # Create a real request with conflicting parameters
    request = app_request(
        path='/users/123?user_id=456',  # Path and query params
        method='POST',
        json={'user_id': '789'}  # Body param
    )
    # Simulate matchdict that would be set by Pyramid routing
    request.matchdict = {'user_id': '123'}
    
    params = context.extract_request_parameters(request)
    assert params['user_id'] == '123'  # Path param wins


def test_query_precedence_over_body(app_request):
    """Test that query parameters take precedence over body."""
    context = ParameterContext('/users')
    
    # Create a real request with both query and body parameters
    request = app_request(
        path='/users?name=query_name',
        method='POST',
        json={'name': 'body_name'}
    )
    
    params = context.extract_request_parameters(request)
    assert params['name'] == 'query_name'  # Query param wins


def test_invalid_json_body_handling(app_request):
    """Test handling of invalid JSON body."""
    context = ParameterContext('/users')
    
    # Create a real request with query params and invalid JSON content type
    request = app_request(
        path='/users?name=John',
        method='POST',
        headers={'Content-Type': 'application/json'},
        # Send invalid JSON by using raw body
        body=b'invalid json{'
    )
    
    # Should not raise exception, just ignore the JSON body and use query params
    params = context.extract_request_parameters(request)
    assert params['name'] == 'John'


def test_convert_integer_parameter():
    """Test converting string to integer."""
    context = ParameterContext('/users/{user_id}')
    
    param_info = ParameterInfo('user_id', int, None, False)
    converted = context._convert_parameter_value('123', param_info, 'user_id')
    
    assert converted == 123
    assert isinstance(converted, int)


def test_convert_float_parameter():
    """Test converting string to float."""
    context = ParameterContext('/items/{price}')
    
    param_info = ParameterInfo('price', float, None, False)
    converted = context._convert_parameter_value('19.99', param_info, 'price')
    
    assert converted == 19.99
    assert isinstance(converted, float)


def test_convert_boolean_parameter_true():
    """Test converting string to boolean (true values)."""
    context = ParameterContext('/items')
    param_info = ParameterInfo('active', bool, None, False)
    
    true_values = ['true', 'True', '1', 'yes', 'on']
    for value in true_values:
        converted = context._convert_parameter_value(value, param_info, 'active')
        assert converted is True


def test_convert_boolean_parameter_false():
    """Test converting string to boolean (false values)."""
    context = ParameterContext('/items')
    param_info = ParameterInfo('active', bool, None, False)
    
    false_values = ['false', 'False', '0', 'no', 'off']
    for value in false_values:
        converted = context._convert_parameter_value(value, param_info, 'active')
        assert converted is False


def test_convert_string_parameter():
    """Test that string parameters pass through unchanged."""
    context = ParameterContext('/users')
    
    param_info = ParameterInfo('name', str, None, False)
    converted = context._convert_parameter_value('John Doe', param_info, 'name')
    
    assert converted == 'John Doe'
    assert isinstance(converted, str)


def test_convert_bytes_parameter():
    """Test converting string to bytes."""
    context = ParameterContext('/data')
    
    param_info = ParameterInfo('data', bytes, None, False)
    converted = context._convert_parameter_value('hello', param_info, 'data')
    
    assert converted == b'hello'
    assert isinstance(converted, bytes)


def test_convert_optional_parameter():
    """Test converting optional parameters."""
    context = ParameterContext('/users')
    
    param_info = ParameterInfo('age', Optional[int], None, False)
    converted = context._convert_parameter_value('25', param_info, 'age')
    
    assert converted == 25
    assert isinstance(converted, int)


def test_conversion_error_handling():
    """Test handling of conversion errors."""
    context = ParameterContext('/users')
    
    param_info = ParameterInfo('age', int, None, False)
    
    with pytest.raises(ValueError, match="Cannot convert parameter 'age'"):
        context._convert_parameter_value('not-a-number', param_info, 'age')


def test_boolean_conversion_error():
    """Test handling of invalid boolean values."""
    context = ParameterContext('/items')
    
    param_info = ParameterInfo('active', bool, None, False)
    
    with pytest.raises(ValueError, match="Cannot convert 'maybe' to boolean"):
        context._convert_parameter_value('maybe', param_info, 'active')


def test_build_simple_arguments(app_request):
    """Test building arguments for a simple function."""
    def test_func(request, user_id: int, name: str):
        return {'user_id': user_id, 'name': name}
    
    signature = inspect_function_signature(test_func)
    context = ParameterContext('/users/{user_id}')
    
    # Create a real request with path and query parameters
    request = app_request(
        path='/users/123?name=John',
        method='GET'
    )
    # Simulate matchdict that would be set by Pyramid routing
    request.matchdict = {'user_id': '123'}
    
    args = context.build_function_arguments(request, signature)
    
    assert args['request'] is request
    assert args['user_id'] == 123
    assert args['name'] == 'John'


def test_build_arguments_with_defaults(app_request):
    """Test building arguments with default values."""
    def test_func(request, name: str, age: int = 25):
        return {'name': name, 'age': age}
    
    signature = inspect_function_signature(test_func)
    context = ParameterContext('/users')
    
    # Create a real request with only name parameter (age not provided)
    request = app_request(
        path='/users?name=John',
        method='GET'
    )
    
    args = context.build_function_arguments(request, signature)
    
    assert args['name'] == 'John'
    assert args['age'] == 25  # Default value


def test_build_arguments_with_optional(app_request):
    """Test building arguments with optional parameters."""
    def test_func(request, name: str, email: Optional[str] = None):
        return {'name': name, 'email': email}
    
    signature = inspect_function_signature(test_func)
    context = ParameterContext('/users')
    
    # Create a real request with only name parameter (email not provided)
    request = app_request(
        path='/users?name=John',
        method='GET'
    )
    
    args = context.build_function_arguments(request, signature)
    
    assert args['name'] == 'John'
    assert args['email'] is None  # Optional parameter becomes None


def test_missing_required_parameter(app_request):
    """Test error when required parameter is missing."""
    def test_func(request, user_id: int, name: str):
        return {'user_id': user_id, 'name': name}
    
    signature = inspect_function_signature(test_func)
    context = ParameterContext('/users/{user_id}')
    
    # Create a real request with only user_id (name is missing)
    request = app_request(
        path='/users/123',
        method='GET'
    )
    # Simulate matchdict that would be set by Pyramid routing
    request.matchdict = {'user_id': '123'}
    
    with pytest.raises(ParameterMissingError, match="Required parameter 'name' is missing"):
        context.build_function_arguments(request, signature)


def test_validate_no_conflicts_valid_case():
    """Test validation with no conflicts."""
    def test_func(request, user_id: int, name: str):
        return {}
    
    signature = inspect_function_signature(test_func)
    context = ParameterContext('/users/{user_id}')
    
    # This should not raise any exceptions
    context.validate_no_conflicts(signature)


def test_missing_path_parameter_in_function():
    """Test error when path parameter is not in function signature."""
    def test_func(request, name: str):  # user_id missing from function
        return {}
    
    signature = inspect_function_signature(test_func)
    context = ParameterContext('/users/{user_id}')  # user_id in path
    
    with pytest.raises(ParameterConflictError, match="Path parameters .* are not present in function signature"):
        context.validate_no_conflicts(signature)


def test_extract_path_parameters_from_pattern():
    """Test extracting path parameters from pattern."""
    params = extract_path_parameters_from_pattern('/users/{user_id}/posts/{post_id}')
    assert params == ['user_id', 'post_id']
    
    params = extract_path_parameters_from_pattern('/simple/path')
    assert params == []
    
    params = extract_path_parameters_from_pattern('/single/{param}')
    assert params == ['param']


def test_validate_path_pattern_valid():
    """Test validating valid path patterns."""
    # These should not raise exceptions
    validate_path_pattern('/users')
    validate_path_pattern('/users/{user_id}')
    validate_path_pattern('/api/v1/users/{user_id}/posts/{post_id}')


def test_validate_path_pattern_invalid():
    """Test validating invalid path patterns."""
    with pytest.raises(ValueError, match="Path pattern must start with '/'"):
        validate_path_pattern('users')
    
    with pytest.raises(ValueError, match="Unbalanced braces"):
        validate_path_pattern('/users/{user_id')
    
    with pytest.raises(ValueError, match="Unbalanced braces"):
        validate_path_pattern('/users/user_id}')
    
    # Note: Empty braces {} are actually valid in our current implementation
    # Let's test a different invalid case
    with pytest.raises(ValueError, match="Invalid parameter name"):
        validate_path_pattern('/users/{user-id}')  # Hyphens not allowed in Python identifiers