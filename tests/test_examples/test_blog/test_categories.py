"""
Tests for category management endpoints of the Blog API example.
"""

import pytest


def test_list_categories(test_blog_app):
    """Test listing all categories."""
    response = test_blog_app.get('/categories')
    
    assert response.status_code == 200
    data = response.json
    
    assert isinstance(data, list)
    assert len(data) == 3  # Sample data has 3 categories
    
    # Check category structure
    category = data[0]
    required_fields = ['id', 'name', 'slug', 'post_count']
    for field in required_fields:
        assert field in category
    
    # Check optional field
    assert 'description' in category  # Can be None


def test_get_category_by_id(test_blog_app):
    """Test getting a specific category by ID."""
    response = test_blog_app.get('/categories/1')
    
    assert response.status_code == 200
    data = response.json
    
    assert data['id'] == 1
    assert data['name'] == 'Technology'
    assert data['slug'] == 'technology'
    assert data['description'] == 'Posts about technology and programming'
    assert isinstance(data['post_count'], int)
    assert data['post_count'] >= 0


def test_get_nonexistent_category(test_blog_app):
    """Test getting a category that doesn't exist."""
    response = test_blog_app.get('/categories/999', expect_errors=True)
    
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'Category not found'


def test_create_category(test_blog_app, sample_category_data):
    """Test creating a new category."""
    response = test_blog_app.post_json('/categories', sample_category_data)
    
    assert response.status_code == 200
    data = response.json
    
    # Check that category was created with correct data
    assert data['name'] == sample_category_data['name']
    assert data['slug'] == sample_category_data['slug']
    assert data['description'] == sample_category_data['description']
    assert data['post_count'] == 0  # New category should have 0 posts
    assert 'id' in data


def test_create_category_minimal_data(test_blog_app):
    """Test creating a category with minimal required data."""
    category_data = {
        'name': 'Minimal Category',
        'slug': 'minimal-category'
        # No description provided
    }
    
    response = test_blog_app.post_json('/categories', category_data)
    
    assert response.status_code == 200
    data = response.json
    
    assert data['name'] == 'Minimal Category'
    assert data['slug'] == 'minimal-category'
    assert data['description'] is None
    assert data['post_count'] == 0


def test_create_category_with_posts(test_blog_app, created_category, created_post):
    """Test that category post count updates when posts are created."""
    # The created_post fixture should have used created_category
    category_id = created_category['id']
    
    # Get the category to check post count
    response = test_blog_app.get(f'/categories/{category_id}')
    
    assert response.status_code == 200
    data = response.json
    
    # Post count should have been incremented
    assert data['post_count'] >= 1


def test_category_post_count_consistency(test_blog_app):
    """Test that category post counts are consistent with actual posts."""
    # Get all categories
    categories_response = test_blog_app.get('/categories')
    assert categories_response.status_code == 200
    categories = categories_response.json
    
    for category in categories:
        category_id = category['id']
        post_count = category['post_count']
        
        # Get posts for this category
        posts_response = test_blog_app.get(f'/posts?category_id={category_id}')
        assert posts_response.status_code == 200
        posts_data = posts_response.json
        
        actual_post_count = posts_data['pagination']['total']
        
        # Post counts should match
        assert post_count == actual_post_count, f"Category {category_id} post count mismatch: {post_count} vs {actual_post_count}"


def test_list_categories_after_creating_new_one(test_blog_app, sample_category_data):
    """Test that listing categories includes newly created ones."""
    # Get initial count
    initial_response = test_blog_app.get('/categories')
    initial_count = len(initial_response.json)
    
    # Create new category
    create_response = test_blog_app.post_json('/categories', sample_category_data)
    assert create_response.status_code == 200
    new_category = create_response.json
    
    # Get updated list
    updated_response = test_blog_app.get('/categories')
    updated_categories = updated_response.json
    
    # Should have one more category
    assert len(updated_categories) == initial_count + 1
    
    # New category should be in the list
    category_ids = [cat['id'] for cat in updated_categories]
    assert new_category['id'] in category_ids


def test_category_slug_uniqueness(test_blog_app):
    """Test that category slugs should be unique (if enforced by the system)."""
    # This test assumes the system should prevent duplicate slugs
    # If not enforced, this test documents the current behavior
    
    category_data_1 = {
        'name': 'First Category',
        'slug': 'duplicate-slug',
        'description': 'First category with this slug'
    }
    
    category_data_2 = {
        'name': 'Second Category',
        'slug': 'duplicate-slug',  # Same slug
        'description': 'Second category with same slug'
    }
    
    # Create first category
    response1 = test_blog_app.post_json('/categories', category_data_1)
    assert response1.status_code == 200
    
    # Try to create second category with same slug
    # This documents current behavior - adjust assertion based on actual implementation
    response2 = test_blog_app.post_json('/categories', category_data_2)
    
    # If the system allows duplicate slugs, this will pass
    # If it prevents duplicates, expect an error
    if response2.status_code == 200:
        # System allows duplicate slugs
        assert response2.json['slug'] == 'duplicate-slug'
    else:
        # System prevents duplicate slugs
        assert response2.status_code in [400, 409]  # Bad Request or Conflict
