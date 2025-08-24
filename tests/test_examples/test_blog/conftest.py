"""
Pytest fixtures for testing the Blog API example.

This module provides fixtures to create and test the Blog API example application
using WebTest for integration testing.
"""

import pytest
from webtest import TestApp
from examples.blog_api.app import create_app
from examples.blog_api.data_store import BlogDataStore


@pytest.fixture
def blog_data_store():
    """Create a fresh BlogDataStore instance for each test."""
    return BlogDataStore()


@pytest.fixture
def blog_app():
    """Create a Pyramid application instance for the Blog API example."""
    # Create the app with a test data store factory
    app = create_app({}, data_store_factory=BlogDataStore)
    return app


@pytest.fixture
def test_blog_app(blog_app):
    """Create a WebTest TestApp instance for making HTTP requests to the blog API."""
    from webtest import TestApp
    return TestApp(blog_app)


@pytest.fixture
def route_names(blog_app):
    """Get list of all registered route names."""
    from pyramid.interfaces import IRoutesMapper
    registry = blog_app.registry
    mapper = registry.queryUtility(IRoutesMapper)
    
    if mapper:
        routes = mapper.get_routes()
        return [route.name for route in routes]
    return []


@pytest.fixture
def route_patterns(blog_app):
    """Get dictionary mapping route names to their patterns."""
    from pyramid.interfaces import IRoutesMapper
    registry = blog_app.registry
    mapper = registry.queryUtility(IRoutesMapper)
    
    if mapper:
        routes = mapper.get_routes()
        return {route.name: route.pattern for route in routes}
    return {}


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'full_name': 'Test User',
        'bio': 'A test user for testing purposes'
    }


@pytest.fixture
def sample_category_data():
    """Sample category data for testing."""
    return {
        'name': 'Test Category',
        'slug': 'test-category',
        'description': 'A test category for testing'
    }


@pytest.fixture
def sample_post_data():
    """Sample post data for testing."""
    return {
        'title': 'Test Post',
        'content': 'This is a test post content with lots of interesting information.',
        'excerpt': 'A test post for testing',
        'author_id': 1,  # Assumes user with ID 1 exists
        'category_id': 1,  # Assumes category with ID 1 exists
        'status': 'published'
    }


@pytest.fixture
def sample_comment_data():
    """Sample comment data for testing."""
    return {
        'content': 'This is a test comment with thoughtful insights.',
        'author_id': 2  # Assumes user with ID 2 exists
    }


@pytest.fixture
def created_user(test_blog_app, sample_user_data):
    """Create a user and return the response data."""
    response = test_blog_app.post_json('/users', sample_user_data)
    assert response.status_code == 200
    return response.json


@pytest.fixture
def created_category(test_blog_app, sample_category_data):
    """Create a category and return the response data."""
    response = test_blog_app.post_json('/categories', sample_category_data)
    assert response.status_code == 200
    return response.json


@pytest.fixture
def created_post(test_blog_app, sample_post_data, created_user, created_category):
    """Create a post and return the response data."""
    # Update post data with actual created user and category IDs
    post_data = sample_post_data.copy()
    post_data['author_id'] = created_user['id']
    post_data['category_id'] = created_category['id']
    
    response = test_blog_app.post_json('/posts', post_data)
    assert response.status_code == 200
    return response.json


@pytest.fixture
def created_comment(test_blog_app, sample_comment_data, created_post, created_user):
    """Create a comment and return the response data."""
    # Use a different user for the comment (user ID 2 from sample data)
    response = test_blog_app.post_json(f'/posts/{created_post["id"]}/comments', sample_comment_data)
    assert response.status_code == 200
    return response.json
