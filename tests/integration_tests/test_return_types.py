"""
Integration tests for different return types.

Tests serialization of various return types: dict, dataclass, lists, optional fields.
"""
from dataclasses import dataclass
from typing import List, Optional
from pyramid_capstone import th_api


@dataclass
class Product:
    """Product model for testing."""
    id: int
    name: str
    price: float
    description: Optional[str] = None


@th_api.get('/return/dict')
def return_dict(request) -> dict:
    """Return a simple dictionary."""
    return {'type': 'dict', 'count': 42, 'active': True}


@th_api.get('/return/dataclass')
def return_dataclass(request) -> Product:
    """Return a dataclass object."""
    return Product(
        id=1,
        name='Test Product',
        price=29.99,
        description='A test product'
    )


@th_api.get('/return/dataclass-optional')
def return_dataclass_with_optional(request) -> Product:
    """Return a dataclass with optional field omitted."""
    return Product(
        id=2,
        name='Product Without Description',
        price=19.99
        # description is None (optional)
    )


@th_api.get('/return/list-dict')
def return_list_of_dicts(request) -> List[dict]:
    """Return a list of dictionaries."""
    return [
        {'id': 1, 'name': 'Item 1'},
        {'id': 2, 'name': 'Item 2'},
        {'id': 3, 'name': 'Item 3'}
    ]


@th_api.get('/return/list-dataclass')
def return_list_of_dataclass(request) -> List[Product]:
    """Return a list of dataclass objects."""
    return [
        Product(id=1, name='Product A', price=10.00, description='First product'),
        Product(id=2, name='Product B', price=20.00),  # No description
        Product(id=3, name='Product C', price=30.00, description='Third product')
    ]


def test_return_dict(app_factory):
    """Test returning a simple dictionary."""
    app = app_factory(scan_packages=[__name__])
    
    response = app.get('/return/dict')
    
    assert response.status_code == 200
    data = response.json
    assert data['type'] == 'dict'
    assert data['count'] == 42
    assert data['active'] is True


def test_return_dataclass(app_factory):
    """Test returning a dataclass object."""
    app = app_factory(scan_packages=[__name__])
    
    response = app.get('/return/dataclass')
    
    assert response.status_code == 200
    data = response.json
    assert data['id'] == 1
    assert data['name'] == 'Test Product'
    assert data['price'] == 29.99
    assert data['description'] == 'A test product'


def test_return_dataclass_with_optional_field(app_factory):
    """Test returning a dataclass with optional field omitted."""
    app = app_factory(scan_packages=[__name__])
    
    response = app.get('/return/dataclass-optional')
    
    assert response.status_code == 200
    data = response.json
    assert data['id'] == 2
    assert data['name'] == 'Product Without Description'
    assert data['price'] == 19.99
    assert data['description'] is None


def test_return_list_of_dicts(app_factory):
    """Test returning a list of dictionaries."""
    app = app_factory(scan_packages=[__name__])
    
    response = app.get('/return/list-dict')
    
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]['id'] == 1
    assert data[0]['name'] == 'Item 1'
    assert data[2]['id'] == 3


def test_return_list_of_dataclass(app_factory):
    """Test returning a list of dataclass objects."""
    app = app_factory(scan_packages=[__name__])
    
    response = app.get('/return/list-dataclass')
    
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) == 3
    
    # First product (with description)
    assert data[0]['id'] == 1
    assert data[0]['name'] == 'Product A'
    assert data[0]['price'] == 10.00
    assert data[0]['description'] == 'First product'
    
    # Second product (no description)
    assert data[1]['id'] == 2
    assert data[1]['name'] == 'Product B'
    assert data[1]['price'] == 20.00
    assert data[1]['description'] is None
    
    # Third product (with description)
    assert data[2]['id'] == 3
    assert data[2]['name'] == 'Product C'
    assert data[2]['price'] == 30.00
    assert data[2]['description'] == 'Third product'
