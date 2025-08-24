"""
Tests for post management endpoints of the Blog API example.
"""


def test_list_posts_default(test_blog_app):
    """Test listing posts with default parameters."""
    response = test_blog_app.get("/posts")

    assert response.status_code == 200
    data = response.json

    assert "posts" in data
    assert "pagination" in data

    posts = data["posts"]
    assert isinstance(posts, list)
    assert len(posts) <= 10  # Default per_page is 10

    # Check post structure
    if posts:
        post = posts[0]
        required_fields = ["id", "title", "slug", "author", "status", "created_at", "view_count"]
        for field in required_fields:
            assert field in post

    # Check pagination structure
    pagination = data["pagination"]
    assert "total" in pagination
    assert "page" in pagination
    assert "per_page" in pagination
    assert "pages" in pagination
    assert "has_next" in pagination
    assert "has_prev" in pagination


def test_list_posts_with_pagination(test_blog_app):
    """Test listing posts with pagination parameters."""
    response = test_blog_app.get("/posts?page=1&per_page=2")

    assert response.status_code == 200
    data = response.json

    posts = data["posts"]
    pagination = data["pagination"]

    assert len(posts) <= 2
    assert pagination["page"] == 1
    assert pagination["per_page"] == 2


def test_list_posts_with_status_filter(test_blog_app):
    """Test listing posts filtered by status."""
    response = test_blog_app.get("/posts?status=published")

    assert response.status_code == 200
    data = response.json

    posts = data["posts"]
    for post in posts:
        assert post["status"] == "published"


def test_list_posts_with_invalid_status(test_blog_app):
    """Test listing posts with invalid status filter."""
    response = test_blog_app.get("/posts?status=invalid_status", expect_errors=True)

    assert response.status_code == 400
    data = response.json
    assert "Invalid status" in data["error"]


def test_list_posts_with_author_filter(test_blog_app, created_post):
    """Test listing posts filtered by author."""
    author_id = created_post["author_id"]

    response = test_blog_app.get(f"/posts?author_id={author_id}")

    assert response.status_code == 200
    data = response.json

    posts = data["posts"]
    for post in posts:
        assert post["author"]["id"] == author_id


def test_list_posts_with_category_filter(test_blog_app, created_post):
    """Test listing posts filtered by category."""
    category_id = created_post["category"]["id"] if created_post["category"] else None

    if category_id:
        response = test_blog_app.get(f"/posts?category_id={category_id}")

        assert response.status_code == 200
        data = response.json

        posts = data["posts"]
        for post in posts:
            if post["category"]:
                assert post["category"]["id"] == category_id


def test_get_post_by_id(test_blog_app, created_post):
    """Test getting a specific post by ID."""
    post_id = created_post["id"]

    response = test_blog_app.get(f"/posts/{post_id}")

    assert response.status_code == 200
    data = response.json

    assert data["id"] == post_id
    assert data["title"] == created_post["title"]
    assert data["content"] == created_post["content"]
    assert data["author_id"] == created_post["author_id"]

    # Check that view count was incremented
    assert data["view_count"] >= created_post["view_count"]


def test_get_post_with_comments(test_blog_app, created_post, created_comment):
    """Test getting a post with comments included."""
    post_id = created_post["id"]

    response = test_blog_app.get(f"/posts/{post_id}?include_comments=true")

    assert response.status_code == 200
    data = response.json

    assert data["id"] == post_id
    assert "comments" in data
    assert isinstance(data["comments"], list)


def test_get_nonexistent_post(test_blog_app):
    """Test getting a post that doesn't exist."""
    response = test_blog_app.get("/posts/999", expect_errors=True)

    assert response.status_code == 404
    data = response.json
    assert data["error"] == "Post not found"


def test_create_post(test_blog_app, sample_post_data, created_user, created_category):
    """Test creating a new post."""
    post_data = sample_post_data.copy()
    post_data["author_id"] = created_user["id"]
    post_data["category_id"] = created_category["id"]

    response = test_blog_app.post_json("/posts", post_data)

    assert response.status_code == 200
    data = response.json

    assert data["title"] == post_data["title"]
    assert data["content"] == post_data["content"]
    assert data["excerpt"] == post_data["excerpt"]
    assert data["author_id"] == post_data["author_id"]
    assert data["category_id"] == post_data["category_id"]
    assert data["status"] == post_data["status"]
    assert "id" in data
    assert "slug" in data
    assert "created_at" in data


def test_create_post_minimal_data(test_blog_app, created_user):
    """Test creating a post with minimal required data."""
    post_data = {
        "title": "Minimal Post",
        "content": "This is minimal post content.",
        "author_id": created_user["id"]
        # No excerpt, category_id, or status (should default to draft)
    }

    response = test_blog_app.post_json("/posts", post_data)

    assert response.status_code == 200
    data = response.json

    assert data["title"] == "Minimal Post"
    assert data["content"] == "This is minimal post content."
    assert data["author_id"] == created_user["id"]
    assert data["excerpt"] is None
    assert data["category_id"] is None
    assert data["status"] == "draft"  # Default status


def test_create_post_with_invalid_author(test_blog_app, sample_post_data):
    """Test creating a post with non-existent author."""
    post_data = sample_post_data.copy()
    post_data["author_id"] = 999  # Non-existent author

    response = test_blog_app.post_json("/posts", post_data, expect_errors=True)

    assert response.status_code == 400
    data = response.json
    assert data["error"] == "Author not found"


def test_create_post_with_invalid_category(test_blog_app, sample_post_data, created_user):
    """Test creating a post with non-existent category."""
    post_data = sample_post_data.copy()
    post_data["author_id"] = created_user["id"]
    post_data["category_id"] = 999  # Non-existent category

    response = test_blog_app.post_json("/posts", post_data, expect_errors=True)

    assert response.status_code == 400
    data = response.json
    assert data["error"] == "Category not found"


def test_create_post_with_invalid_status(test_blog_app, sample_post_data, created_user):
    """Test creating a post with invalid status."""
    post_data = sample_post_data.copy()
    post_data["author_id"] = created_user["id"]
    post_data["status"] = "invalid_status"

    response = test_blog_app.post_json("/posts", post_data, expect_errors=True)

    assert response.status_code == 400
    data = response.json
    assert "Invalid status" in data["error"]


def test_update_post(test_blog_app, created_post):
    """Test updating a post."""
    post_id = created_post["id"]
    update_data = {
        "title": "Updated Post Title",
        "content": "Updated post content with new information.",
        "excerpt": "Updated excerpt",
        "status": "published",
    }

    response = test_blog_app.put_json(f"/posts/{post_id}", update_data)

    assert response.status_code == 200
    data = response.json

    assert data["id"] == post_id
    assert data["title"] == "Updated Post Title"
    assert data["content"] == "Updated post content with new information."
    assert data["excerpt"] == "Updated excerpt"
    assert data["status"] == "published"
    # Original fields should remain
    assert data["author_id"] == created_post["author_id"]


def test_update_post_partial(test_blog_app, created_post):
    """Test updating a post with partial data."""
    post_id = created_post["id"]
    update_data = {"title": "Partially Updated Title"}

    response = test_blog_app.put_json(f"/posts/{post_id}", update_data)

    assert response.status_code == 200
    data = response.json

    assert data["id"] == post_id
    assert data["title"] == "Partially Updated Title"
    # Other fields should remain unchanged
    assert data["content"] == created_post["content"]
    assert data["author_id"] == created_post["author_id"]


def test_update_nonexistent_post(test_blog_app):
    """Test updating a post that doesn't exist."""
    update_data = {"title": "Updated Title"}

    response = test_blog_app.put_json("/posts/999", update_data, expect_errors=True)

    assert response.status_code == 404
    data = response.json
    assert data["error"] == "Post not found"


def test_update_post_with_invalid_category(test_blog_app, created_post):
    """Test updating a post with non-existent category."""
    post_id = created_post["id"]
    update_data = {"category_id": 999}  # Non-existent category

    response = test_blog_app.put_json(f"/posts/{post_id}", update_data, expect_errors=True)

    assert response.status_code == 400
    data = response.json
    assert data["error"] == "Category not found"


def test_delete_post(test_blog_app, created_post):
    """Test deleting a post."""
    post_id = created_post["id"]

    response = test_blog_app.delete(f"/posts/{post_id}")

    assert response.status_code == 200
    data = response.json

    assert data["deleted"] is True
    assert data["post_id"] == post_id

    # Verify post is actually deleted
    get_response = test_blog_app.get(f"/posts/{post_id}", expect_errors=True)
    assert get_response.status_code == 404


def test_delete_nonexistent_post(test_blog_app):
    """Test deleting a post that doesn't exist."""
    response = test_blog_app.delete("/posts/999", expect_errors=True)

    assert response.status_code == 404
    data = response.json
    assert data["error"] == "Post not found"
