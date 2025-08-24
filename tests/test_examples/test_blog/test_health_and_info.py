"""
Tests for health check and informational endpoints of the Blog API example.
"""

import pytest


def test_health_check(test_blog_app):
    """Test the health check endpoint."""
    response = test_blog_app.get('/health')
    
    assert response.status_code == 200
    data = response.json
    
    # Check required fields
    assert data['status'] == 'healthy'
    assert data['service'] == 'blog-api'
    assert data['version'] == '1.0.0'
    
    # Check counts (should have sample data)
    assert data['users_count'] == 3
    assert data['posts_count'] == 3
    assert data['categories_count'] == 3
    assert data['comments_count'] == 3


def test_root_endpoint(test_blog_app):
    """Test the root endpoint that provides API information."""
    response = test_blog_app.get('/')
    
    assert response.status_code == 200
    data = response.json
    
    # Check basic information
    assert data['message'] == 'Welcome to the Blog API Example'
    assert 'pyramid-capstone' in data['description']
    assert data['version'] == '1.0.0'
    
    # Check documentation links
    assert 'documentation' in data
    doc = data['documentation']
    assert doc['swagger_ui'] == '/swagger-ui/'
    assert doc['redoc'] == '/redoc/'
    assert doc['openapi_json'] == '/openapi.json'
    
    # Check quick links
    assert 'quick_links' in data
    links = data['quick_links']
    assert links['health_check'] == '/health'
    assert links['blog_statistics'] == '/stats'
    
    # Check features demonstrated
    assert 'features_demonstrated' in data
    features = data['features_demonstrated']
    assert 'Type-hinted API endpoints with automatic validation' in features
    assert 'CRUD operations for multiple entities (users, posts, categories, comments)' in features
    assert 'Automatic OpenAPI documentation generation' in features


def test_blog_statistics(test_blog_app):
    """Test the blog statistics endpoint."""
    response = test_blog_app.get('/stats')
    
    assert response.status_code == 200
    data = response.json
    
    # Check structure
    assert 'users' in data
    assert 'posts' in data
    assert 'categories' in data
    assert 'comments' in data
    
    # Check user stats
    users = data['users']
    assert users['total'] == 3
    assert users['active'] == 3  # All sample users are active
    
    # Check post stats
    posts = data['posts']
    assert posts['total'] == 3
    assert posts['published'] >= 0
    assert posts['drafts'] >= 0
    assert posts['archived'] >= 0
    assert posts['published'] + posts['drafts'] + posts['archived'] == posts['total']
    
    # Check category stats
    categories = data['categories']
    assert categories['total'] == 3
    
    # Check comment stats
    comments = data['comments']
    assert comments['total'] == 3
