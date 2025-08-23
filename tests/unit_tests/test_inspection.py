"""
Tests for the function signature inspection module.

This module tests the inspection utilities that extract type hints
and parameter information from function signatures.
"""

import pytest
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
from pyramid_type_hinted_api.inspection import (
    inspect_function_signature,
    ParameterInfo,
    FunctionSignature,
    is_list_type,
    get_list_item_type,
    is_basic_type,
    validate_type_compatibility
)


@dataclass
class SampleDataClass:
    """Sample dataclass for testing complex types."""
    name: str
    age: int
    active: bool = True


def test_parameter_info_creation():
    """Test creating ParameterInfo instances."""
    param = ParameterInfo(
        name='test_param',
        type_hint=int,
        default=None,
        has_default=False
    )
    
    assert param.name == 'test_param'
    assert param.type_hint is int
    assert param.default is None
    assert param.has_default is False


def test_parameter_info_is_optional_with_optional_type():
    """Test is_optional property with Optional types."""
    optional_param = ParameterInfo(
        name='optional_param',
        type_hint=Optional[str],
        default=None,
        has_default=False
    )
    
    assert optional_param.is_optional is True


def test_parameter_info_is_optional_with_regular_type():
    """Test is_optional property with regular types."""
    regular_param = ParameterInfo(
        name='regular_param',
        type_hint=str,
        default=None,
        has_default=False
    )
    
    assert regular_param.is_optional is False


def test_parameter_info_inner_type_with_optional():
    """Test inner_type property with Optional types."""
    optional_param = ParameterInfo(
        name='optional_param',
        type_hint=Optional[int],
        default=None,
        has_default=False
    )
    
    assert optional_param.inner_type is int


def test_parameter_info_inner_type_with_regular_type():
    """Test inner_type property with regular types."""
    regular_param = ParameterInfo(
        name='regular_param',
        type_hint=str,
        default=None,
        has_default=False
    )
    
    assert regular_param.inner_type is str


def test_function_signature_creation():
    """Test creating FunctionSignature instances."""
    params = {
        'param1': ParameterInfo('param1', int, None, False),
        'param2': ParameterInfo('param2', str, 'default', True)
    }
    
    signature = FunctionSignature(
        parameters=params,
        return_type=dict,
        has_request_param=True
    )
    
    assert len(signature.parameters) == 2
    assert signature.return_type is dict
    assert signature.has_request_param is True


def test_function_signature_get_non_request_parameters():
    """Test filtering out request parameter."""
    params = {
        'request': ParameterInfo('request', Any, None, False),
        'user_id': ParameterInfo('user_id', int, None, False),
        'name': ParameterInfo('name', str, None, False)
    }
    
    signature = FunctionSignature(
        parameters=params,
        return_type=None,
        has_request_param=True
    )
    
    non_request_params = signature.get_non_request_parameters()
    assert 'request' not in non_request_params
    assert 'user_id' in non_request_params
    assert 'name' in non_request_params
    assert len(non_request_params) == 2


def test_function_signature_get_required_parameters():
    """Test getting required parameters."""
    params = {
        'required_param': ParameterInfo('required_param', int, None, False),
        'optional_param': ParameterInfo('optional_param', Optional[str], None, False),
        'default_param': ParameterInfo('default_param', str, 'default', True)
    }
    
    signature = FunctionSignature(
        parameters=params,
        return_type=None,
        has_request_param=True
    )
    
    required_params = signature.get_required_parameters()
    assert 'required_param' in required_params
    assert 'optional_param' not in required_params
    assert 'default_param' not in required_params
    assert len(required_params) == 1


def test_function_signature_get_optional_parameters():
    """Test getting optional parameters."""
    params = {
        'required_param': ParameterInfo('required_param', int, None, False),
        'optional_param': ParameterInfo('optional_param', Optional[str], None, False),
        'default_param': ParameterInfo('default_param', str, 'default', True)
    }
    
    signature = FunctionSignature(
        parameters=params,
        return_type=None,
        has_request_param=True
    )
    
    optional_params = signature.get_optional_parameters()
    assert 'required_param' not in optional_params
    assert 'optional_param' in optional_params
    assert 'default_param' in optional_params
    assert len(optional_params) == 2


def test_inspect_simple_function():
    """Test inspecting a simple function."""
    def simple_func(request, user_id: int, name: str) -> dict:
        return {'user_id': user_id, 'name': name}
    
    signature = inspect_function_signature(simple_func)
    
    assert signature.has_request_param is True
    assert signature.return_type is dict
    
    params = signature.get_non_request_parameters()
    assert len(params) == 2
    assert 'user_id' in params
    assert 'name' in params
    assert params['user_id'].type_hint is int
    assert params['name'].type_hint is str


def test_inspect_function_with_optional_parameters():
    """Test inspecting function with optional parameters."""
    def func_with_optional(request, required: int, optional: Optional[str] = None) -> dict:
        return {'required': required, 'optional': optional}
    
    signature = inspect_function_signature(func_with_optional)
    
    params = signature.get_non_request_parameters()
    assert len(params) == 2
    
    required_param = params['required']
    assert required_param.type_hint is int
    assert not required_param.has_default
    assert not required_param.is_optional
    
    optional_param = params['optional']
    assert optional_param.type_hint == Optional[str]
    assert optional_param.has_default
    assert optional_param.is_optional
    assert optional_param.default is None


def test_inspect_function_with_default_values():
    """Test inspecting function with default values."""
    def func_with_defaults(request, name: str, age: int = 25, active: bool = True):
        return {'name': name, 'age': age, 'active': active}
    
    signature = inspect_function_signature(func_with_defaults)
    
    params = signature.get_non_request_parameters()
    
    name_param = params['name']
    assert not name_param.has_default
    
    age_param = params['age']
    assert age_param.has_default
    assert age_param.default == 25
    
    active_param = params['active']
    assert active_param.has_default
    assert active_param.default is True


def test_inspect_function_with_complex_types():
    """Test inspecting function with complex types."""
    def func_with_complex_types(
        request, 
        items: List[str], 
        metadata: Dict[str, Any],
        user: SampleDataClass
    ) -> List[dict]:
        return [{'items': items, 'metadata': metadata, 'user': user}]
    
    signature = inspect_function_signature(func_with_complex_types)
    
    params = signature.get_non_request_parameters()
    assert params['items'].type_hint == List[str]
    assert params['metadata'].type_hint == Dict[str, Any]
    assert params['user'].type_hint is SampleDataClass
    assert signature.return_type == List[dict]


def test_inspect_function_without_request_parameter():
    """Test that functions without request parameter raise error."""
    def func_without_request(user_id: int) -> dict:
        return {'user_id': user_id}
    
    with pytest.raises(ValueError, match="must have a 'request' parameter"):
        inspect_function_signature(func_without_request)


def test_inspect_function_with_missing_type_hints():
    """Test that functions with missing type hints raise error."""
    def func_missing_hints(request, user_id):  # Missing type hint
        return {'user_id': user_id}
    
    with pytest.raises(ValueError, match="must have a type hint"):
        inspect_function_signature(func_missing_hints)


def test_inspect_function_with_basic_types():
    """Test handling of basic type hints."""
    def func_with_basic_types(request, name: str, age: int) -> dict:
        return {'name': name, 'age': age}
    
    # This should work fine
    signature = inspect_function_signature(func_with_basic_types)
    assert signature is not None


def test_is_list_type():
    """Test is_list_type function."""
    assert is_list_type(List[str]) is True
    assert is_list_type(List[int]) is True
    # Note: plain 'list' without type args is not considered a List type in our system
    assert is_list_type(str) is False
    assert is_list_type(int) is False
    assert is_list_type(Dict[str, int]) is False


def test_get_list_item_type():
    """Test get_list_item_type function."""
    assert get_list_item_type(List[str]) is str
    assert get_list_item_type(List[int]) is int
    assert get_list_item_type(List[SampleDataClass]) is SampleDataClass
    assert get_list_item_type(str) is None
    assert get_list_item_type(list) is None  # No type args


@pytest.mark.parametrize("type_hint", [
    int, str, float, bool, bytes, list, dict
])
def test_is_basic_type_with_basic_types(type_hint):
    """Test is_basic_type function with basic types."""
    assert is_basic_type(type_hint) is True


@pytest.mark.parametrize("type_hint", [
    SampleDataClass, List[int], Optional[str], Union[int, str]
])
def test_is_basic_type_with_non_basic_types(type_hint):
    """Test is_basic_type function with non-basic types."""
    assert is_basic_type(type_hint) is False


def test_validate_type_compatibility():
    """Test validate_type_compatibility function."""
    # These should not raise exceptions
    validate_type_compatibility(int, 'test_param')
    validate_type_compatibility(str, 'test_param')
    validate_type_compatibility(Optional[int], 'test_param')
    validate_type_compatibility(List[str], 'test_param')
    validate_type_compatibility(SampleDataClass, 'test_param')
    
    # This should also not raise (we're permissive with unknown types)
    validate_type_compatibility(Any, 'test_param')


def test_inspect_function_with_no_parameters():
    """Test function with only request parameter."""
    def func_no_params(request) -> dict:
        return {}
    
    signature = inspect_function_signature(func_no_params)
    assert signature.has_request_param is True
    assert len(signature.get_non_request_parameters()) == 0
    assert signature.return_type is dict


def test_inspect_function_with_no_return_type():
    """Test function without return type annotation."""
    def func_no_return(request, name: str):
        return {'name': name}
    
    signature = inspect_function_signature(func_no_return)
    assert signature.return_type is None
    assert len(signature.get_non_request_parameters()) == 1


def test_inspect_function_with_args_and_kwargs():
    """Test that functions with *args and **kwargs are not supported."""
    def func_with_varargs(request, name: str, *args, **kwargs) -> dict:
        return {'name': name, 'args': args, 'kwargs': kwargs}
    
    # This should raise an error because *args and **kwargs don't have type hints
    with pytest.raises(ValueError, match="must have a type hint"):
        inspect_function_signature(func_with_varargs)