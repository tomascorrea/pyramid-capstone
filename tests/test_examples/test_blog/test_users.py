"""
Tests for user management endpoints of the Blog API example.
"""

import pytest


def test_list_users(test_blog_app):
    """Test listing all users."""
    response = test_blog_app.get('/users')
    
    assert response.status_code == 200
    data = response.json
    
    assert isinstance(data, list)
    assert len(data) == 3  # Sample data has 3 users
    
    # Check user structure
    user = data[0]
    required_fields = ['id', 'username', 'email', 'full_name', 'is_active', 'created_at']
    for field in required_fields:
        assert field in user
    
    # Check optional field
    assert 'bio' in user  # Can be None


def test_get_user_by_id(test_blog_app):
    """Test getting a specific user by ID."""
    response = test_blog_app.get('/users/1')
    
    assert response.status_code == 200
    data = response.json
    
    assert data['id'] == 1
    assert data['username'] == 'john_doe'
    assert data['email'] == 'john@example.com'
    assert data['full_name'] == 'John Doe'
    assert data['is_active'] is True
    assert data['bio'] == 'Tech enthusiast and blogger'


def test_get_nonexistent_user(test_blog_app):
    """Test getting a user that doesn't exist."""
    response = test_blog_app.get('/users/999', expect_errors=True)
    
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'User not found'


def test_create_user(test_blog_app, sample_user_data):
    """Test creating a new user."""
    response = test_blog_app.post_json('/users', sample_user_data)
    
    assert response.status_code == 200
    data = response.json
    
    # Check that user was created with correct data
    assert data['username'] == sample_user_data['username']
    assert data['email'] == sample_user_data['email']
    assert data['full_name'] == sample_user_data['full_name']
    assert data['bio'] == sample_user_data['bio']
    assert data['is_active'] is True
    assert 'id' in data
    assert 'created_at' in data


def test_create_user_minimal_data(test_blog_app):
    """Test creating a user with minimal required data."""
    user_data = {
        'username': 'minimal_user',
        'email': 'minimal@example.com',
        'full_name': 'Minimal User'
        # No bio provided
    }
    
    response = test_blog_app.post_json('/users', user_data)
    
    assert response.status_code == 200
    data = response.json
    
    assert data['username'] == 'minimal_user'
    assert data['email'] == 'minimal@example.com'
    assert data['full_name'] == 'Minimal User'
    assert data['bio'] is None
    assert data['is_active'] is True


def test_update_user(test_blog_app, created_user):
    """Test updating a user."""
    user_id = created_user['id']
    update_data = {
        'full_name': 'Updated Test User',
        'bio': 'Updated bio for testing',
        'is_active': False
    }
    
    response = test_blog_app.put_json(f'/users/{user_id}', update_data)
    
    assert response.status_code == 200
    data = response.json
    
    assert data['id'] == user_id
    assert data['full_name'] == 'Updated Test User'
    assert data['bio'] == 'Updated bio for testing'
    assert data['is_active'] is False
    # Original fields should remain unchanged
    assert data['username'] == created_user['username']
    assert data['email'] == created_user['email']


def test_update_user_partial(test_blog_app, created_user):
    """Test updating a user with partial data."""
    user_id = created_user['id']
    update_data = {
        'bio': 'Only updating the bio'
    }
    
    response = test_blog_app.put_json(f'/users/{user_id}', update_data)
    
    assert response.status_code == 200
    data = response.json
    
    assert data['id'] == user_id
    assert data['bio'] == 'Only updating the bio'
    # Other fields should remain unchanged
    assert data['full_name'] == created_user['full_name']
    assert data['username'] == created_user['username']
    assert data['email'] == created_user['email']
    assert data['is_active'] == created_user['is_active']


def test_update_nonexistent_user(test_blog_app):
    """Test updating a user that doesn't exist."""
    update_data = {'full_name': 'Updated Name'}
    
    response = test_blog_app.put_json('/users/999', update_data, expect_errors=True)
    
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'User not found'


def test_delete_user(test_blog_app, created_user):
    """Test deleting a user."""
    user_id = created_user['id']
    
    response = test_blog_app.delete(f'/users/{user_id}')
    
    assert response.status_code == 200
    data = response.json
    
    assert data['deleted'] is True
    assert data['user_id'] == user_id
    
    # Verify user is actually deleted
    get_response = test_blog_app.get(f'/users/{user_id}', expect_errors=True)
    assert get_response.status_code == 404


def test_delete_nonexistent_user(test_blog_app):
    """Test deleting a user that doesn't exist."""
    response = test_blog_app.delete('/users/999', expect_errors=True)
    
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'User not found'


def test_get_user_posts(test_blog_app, created_post):
    """Test getting posts by a specific user."""
    user_id = created_post['author_id']
    
    response = test_blog_app.get(f'/users/{user_id}/posts')
    
    assert response.status_code == 200
    data = response.json
    
    assert 'posts' in data
    assert 'pagination' in data
    
    posts = data['posts']
    assert isinstance(posts, list)
    
    # Check pagination structure
    pagination = data['pagination']
    assert 'total' in pagination
    assert 'page' in pagination
    assert 'per_page' in pagination
    assert 'pages' in pagination
    assert 'has_next' in pagination
    assert 'has_prev' in pagination


def test_get_user_posts_with_pagination(test_blog_app, created_post):
    """Test getting user posts with pagination parameters."""
    user_id = created_post['author_id']
    
    response = test_blog_app.get(f'/users/{user_id}/posts?page=1&per_page=2')
    
    assert response.status_code == 200
    data = response.json
    
    pagination = data['pagination']
    assert pagination['page'] == 1
    assert pagination['per_page'] == 2


def test_get_posts_for_nonexistent_user(test_blog_app):
    """Test getting posts for a user that doesn't exist."""
    response = test_blog_app.get('/users/999/posts', expect_errors=True)
    
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'User not found'
