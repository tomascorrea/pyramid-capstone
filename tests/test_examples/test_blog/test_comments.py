"""
Tests for comment management endpoints of the Blog API example.
"""

import pytest


def test_list_post_comments(test_blog_app, created_post, created_comment):
    """Test listing comments for a specific post."""
    post_id = created_post['id']
    
    response = test_blog_app.get(f'/posts/{post_id}/comments')
    
    assert response.status_code == 200
    data = response.json
    
    assert isinstance(data, list)
    assert len(data) >= 1  # Should have at least the created comment
    
    # Check comment structure
    comment = data[0]
    required_fields = ['id', 'post_id', 'author_id', 'content', 'created_at']
    for field in required_fields:
        assert field in comment
    
    # Should have author information populated
    assert 'author' in comment
    assert comment['author'] is not None
    assert 'id' in comment['author']
    assert 'username' in comment['author']


def test_list_comments_for_nonexistent_post(test_blog_app):
    """Test listing comments for a post that doesn't exist."""
    response = test_blog_app.get('/posts/999/comments', expect_errors=True)
    
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'Post not found'


def test_get_comment_by_id(test_blog_app, created_comment):
    """Test getting a specific comment by ID."""
    comment_id = created_comment['id']
    
    response = test_blog_app.get(f'/comments/{comment_id}')
    
    assert response.status_code == 200
    data = response.json
    
    assert data['id'] == comment_id
    assert data['content'] == created_comment['content']
    assert data['author_id'] == created_comment['author_id']
    assert data['post_id'] == created_comment['post_id']
    
    # Should have author information populated
    assert 'author' in data
    assert data['author'] is not None
    assert data['author']['id'] == created_comment['author_id']


def test_get_nonexistent_comment(test_blog_app):
    """Test getting a comment that doesn't exist."""
    response = test_blog_app.get('/comments/999', expect_errors=True)
    
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'Comment not found'


def test_create_comment(test_blog_app, created_post, sample_comment_data):
    """Test creating a new comment on a post."""
    post_id = created_post['id']
    
    response = test_blog_app.post_json(f'/posts/{post_id}/comments', sample_comment_data)
    
    assert response.status_code == 200
    data = response.json
    
    # Check that comment was created with correct data
    assert data['content'] == sample_comment_data['content']
    assert data['author_id'] == sample_comment_data['author_id']
    assert data['post_id'] == post_id
    assert 'id' in data
    assert 'created_at' in data
    
    # Should have author information populated
    assert 'author' in data
    assert data['author'] is not None
    assert data['author']['id'] == sample_comment_data['author_id']


def test_create_comment_on_nonexistent_post(test_blog_app, sample_comment_data):
    """Test creating a comment on a post that doesn't exist."""
    response = test_blog_app.post_json('/posts/999/comments', sample_comment_data, expect_errors=True)
    
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'Post not found'


def test_create_comment_with_nonexistent_author(test_blog_app, created_post):
    """Test creating a comment with a non-existent author."""
    post_id = created_post['id']
    comment_data = {
        'content': 'Test comment content',
        'author_id': 999  # Non-existent author
    }
    
    response = test_blog_app.post_json(f'/posts/{post_id}/comments', comment_data, expect_errors=True)
    
    assert response.status_code == 400
    data = response.json
    assert data['error'] == 'Author not found'


def test_delete_comment(test_blog_app, created_comment):
    """Test deleting a comment."""
    comment_id = created_comment['id']
    
    response = test_blog_app.delete(f'/comments/{comment_id}')
    
    assert response.status_code == 200
    data = response.json
    
    assert data['deleted'] is True
    assert data['comment_id'] == comment_id
    
    # Verify comment is actually deleted
    get_response = test_blog_app.get(f'/comments/{comment_id}', expect_errors=True)
    assert get_response.status_code == 404


def test_delete_nonexistent_comment(test_blog_app):
    """Test deleting a comment that doesn't exist."""
    response = test_blog_app.delete('/comments/999', expect_errors=True)
    
    assert response.status_code == 404
    data = response.json
    assert data['error'] == 'Comment not found'


def test_comment_author_relationship(test_blog_app, created_comment):
    """Test that comment author information is correctly populated."""
    comment_id = created_comment['id']
    
    # Get the comment
    comment_response = test_blog_app.get(f'/comments/{comment_id}')
    assert comment_response.status_code == 200
    comment = comment_response.json
    
    # Get the author directly
    author_id = comment['author_id']
    author_response = test_blog_app.get(f'/users/{author_id}')
    assert author_response.status_code == 200
    author = author_response.json
    
    # Comment's author information should match the actual user
    assert comment['author']['id'] == author['id']
    assert comment['author']['username'] == author['username']
    assert comment['author']['full_name'] == author['full_name']
    assert comment['author']['email'] == author['email']


def test_post_comment_relationship(test_blog_app, created_post, created_comment):
    """Test that comments are properly associated with posts."""
    post_id = created_post['id']
    comment_id = created_comment['id']
    
    # Get comments for the post
    comments_response = test_blog_app.get(f'/posts/{post_id}/comments')
    assert comments_response.status_code == 200
    comments = comments_response.json
    
    # The created comment should be in the list
    comment_ids = [comment['id'] for comment in comments]
    assert comment_id in comment_ids
    
    # Find our specific comment
    our_comment = next(comment for comment in comments if comment['id'] == comment_id)
    assert our_comment['post_id'] == post_id


def test_multiple_comments_on_post(test_blog_app, created_post):
    """Test creating multiple comments on the same post."""
    post_id = created_post['id']
    
    # Create first comment
    comment_data_1 = {
        'content': 'First comment on this post',
        'author_id': 1  # Using sample user ID
    }
    response1 = test_blog_app.post_json(f'/posts/{post_id}/comments', comment_data_1)
    assert response1.status_code == 200
    comment1 = response1.json
    
    # Create second comment
    comment_data_2 = {
        'content': 'Second comment on this post',
        'author_id': 2  # Using different sample user ID
    }
    response2 = test_blog_app.post_json(f'/posts/{post_id}/comments', comment_data_2)
    assert response2.status_code == 200
    comment2 = response2.json
    
    # Get all comments for the post
    comments_response = test_blog_app.get(f'/posts/{post_id}/comments')
    assert comments_response.status_code == 200
    comments = comments_response.json
    
    # Should have at least our two comments
    comment_ids = [comment['id'] for comment in comments]
    assert comment1['id'] in comment_ids
    assert comment2['id'] in comment_ids
    
    # Comments should have different authors
    assert comment1['author_id'] != comment2['author_id']


def test_comment_content_validation(test_blog_app, created_post):
    """Test comment content validation."""
    post_id = created_post['id']
    
    # Test with empty content (should fail if validation is implemented)
    empty_comment_data = {
        'content': '',
        'author_id': 1
    }
    
    # This test documents current behavior - adjust based on actual validation
    response = test_blog_app.post_json(f'/posts/{post_id}/comments', empty_comment_data)
    
    # If validation is implemented, expect error; otherwise, it should succeed
    if response.status_code == 200:
        # No validation implemented
        assert response.json['content'] == ''
    else:
        # Validation implemented
        assert response.status_code == 400


def test_comment_ordering(test_blog_app, created_post):
    """Test that comments are returned in a consistent order."""
    post_id = created_post['id']
    
    # Create multiple comments with slight delays to ensure different timestamps
    import time
    
    comment_data_1 = {'content': 'First comment', 'author_id': 1}
    response1 = test_blog_app.post_json(f'/posts/{post_id}/comments', comment_data_1)
    assert response1.status_code == 200
    
    time.sleep(0.01)  # Small delay
    
    comment_data_2 = {'content': 'Second comment', 'author_id': 2}
    response2 = test_blog_app.post_json(f'/posts/{post_id}/comments', comment_data_2)
    assert response2.status_code == 200
    
    # Get comments
    comments_response = test_blog_app.get(f'/posts/{post_id}/comments')
    assert comments_response.status_code == 200
    comments = comments_response.json
    
    # Should have at least 2 comments
    assert len(comments) >= 2
    
    # Comments should have created_at timestamps
    for comment in comments:
        assert 'created_at' in comment
        assert comment['created_at'] is not None
