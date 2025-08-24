"""
Integration tests for the complete Blog API workflow.

These tests verify that the entire system works together correctly,
testing realistic user scenarios and data flows.
"""


def test_complete_blog_workflow(test_blog_app):
    """Test a complete blog workflow from user creation to commenting."""

    # 1. Create a user (author)
    author_data = {
        "username": "blog_author",
        "email": "author@blog.com",
        "full_name": "Blog Author",
        "bio": "Professional blogger and writer",
    }
    author_response = test_blog_app.post_json("/users", author_data)
    assert author_response.status_code == 200
    author = author_response.json

    # 2. Create another user (commenter)
    commenter_data = {"username": "blog_reader", "email": "reader@blog.com", "full_name": "Blog Reader"}
    commenter_response = test_blog_app.post_json("/users", commenter_data)
    assert commenter_response.status_code == 200
    commenter = commenter_response.json

    # 3. Create a category
    category_data = {
        "name": "Web Development",
        "slug": "web-development",
        "description": "Articles about web development technologies",
    }
    category_response = test_blog_app.post_json("/categories", category_data)
    assert category_response.status_code == 200
    category = category_response.json

    # 4. Create a blog post
    post_data = {
        "title": "Getting Started with Pyramid",
        "content": "Pyramid is a powerful Python web framework that provides...",
        "excerpt": "Learn the basics of Pyramid web framework",
        "author_id": author["id"],
        "category_id": category["id"],
        "status": "published",
    }
    post_response = test_blog_app.post_json("/posts", post_data)
    assert post_response.status_code == 200
    post = post_response.json

    # 5. Verify the post appears in listings
    posts_response = test_blog_app.get("/posts?status=published")
    assert posts_response.status_code == 200
    posts_data = posts_response.json
    post_ids = [p["id"] for p in posts_data["posts"]]
    assert post["id"] in post_ids

    # 6. Verify the post appears in author's posts
    author_posts_response = test_blog_app.get(f'/users/{author["id"]}/posts')
    assert author_posts_response.status_code == 200
    author_posts_data = author_posts_response.json
    author_post_ids = [p["id"] for p in author_posts_data["posts"]]
    assert post["id"] in author_post_ids

    # 7. Add a comment to the post
    comment_data = {"content": "Great article! Very helpful for beginners.", "author_id": commenter["id"]}
    comment_response = test_blog_app.post_json(f'/posts/{post["id"]}/comments', comment_data)
    assert comment_response.status_code == 200
    comment = comment_response.json

    # 8. Verify the comment appears in post comments
    comments_response = test_blog_app.get(f'/posts/{post["id"]}/comments')
    assert comments_response.status_code == 200
    comments = comments_response.json
    comment_ids = [c["id"] for c in comments]
    assert comment["id"] in comment_ids

    # 9. Get the post with comments included
    post_with_comments_response = test_blog_app.get(f'/posts/{post["id"]}?include_comments=true')
    assert post_with_comments_response.status_code == 200
    post_with_comments = post_with_comments_response.json
    assert "comments" in post_with_comments
    assert len(post_with_comments["comments"]) >= 1

    # 10. Update the post
    update_data = {
        "title": "Getting Started with Pyramid - Updated",
        "content": "Pyramid is a powerful Python web framework that provides... [Updated content]",
        "status": "published",
    }
    update_response = test_blog_app.put_json(f'/posts/{post["id"]}', update_data)
    assert update_response.status_code == 200
    updated_post = update_response.json
    assert updated_post["title"] == "Getting Started with Pyramid - Updated"

    # 11. Check blog statistics
    stats_response = test_blog_app.get("/stats")
    assert stats_response.status_code == 200
    stats = stats_response.json

    # Should reflect our created content
    assert stats["users"]["total"] >= 2  # Our 2 users + sample data
    assert stats["posts"]["total"] >= 1  # Our post + sample data
    assert stats["categories"]["total"] >= 1  # Our category + sample data
    assert stats["comments"]["total"] >= 1  # Our comment + sample data


def test_pagination_workflow(test_blog_app):
    """Test pagination across different endpoints."""

    # Create multiple posts to test pagination
    author_data = {"username": "prolific_author", "email": "prolific@blog.com", "full_name": "Prolific Author"}
    author_response = test_blog_app.post_json("/users", author_data)
    assert author_response.status_code == 200
    author = author_response.json

    # Create 5 posts
    created_posts = []
    for i in range(5):
        post_data = {
            "title": f"Test Post {i+1}",
            "content": f"Content for test post number {i+1}",
            "author_id": author["id"],
            "status": "published",
        }
        post_response = test_blog_app.post_json("/posts", post_data)
        assert post_response.status_code == 200
        created_posts.append(post_response.json)

    # Test pagination with per_page=2
    page1_response = test_blog_app.get("/posts?per_page=2&page=1")
    assert page1_response.status_code == 200
    page1_data = page1_response.json

    assert len(page1_data["posts"]) <= 2
    assert page1_data["pagination"]["page"] == 1
    assert page1_data["pagination"]["per_page"] == 2
    assert page1_data["pagination"]["total"] >= 5  # Our posts + sample data

    # Test second page
    page2_response = test_blog_app.get("/posts?per_page=2&page=2")
    assert page2_response.status_code == 200
    page2_data = page2_response.json

    assert page2_data["pagination"]["page"] == 2
    assert page2_data["pagination"]["per_page"] == 2

    # Posts on different pages should be different
    page1_ids = [p["id"] for p in page1_data["posts"]]
    page2_ids = [p["id"] for p in page2_data["posts"]]
    assert not set(page1_ids).intersection(set(page2_ids))


def test_filtering_workflow(test_blog_app):
    """Test filtering across different endpoints."""

    # Create users
    author1_data = {"username": "author1", "email": "author1@test.com", "full_name": "Author One"}
    author1_response = test_blog_app.post_json("/users", author1_data)
    author1 = author1_response.json

    author2_data = {"username": "author2", "email": "author2@test.com", "full_name": "Author Two"}
    author2_response = test_blog_app.post_json("/users", author2_data)
    author2 = author2_response.json

    # Create categories
    tech_category_data = {"name": "Technology", "slug": "tech-test"}
    tech_category_response = test_blog_app.post_json("/categories", tech_category_data)
    tech_category = tech_category_response.json

    lifestyle_category_data = {"name": "Lifestyle", "slug": "lifestyle-test"}
    lifestyle_category_response = test_blog_app.post_json("/categories", lifestyle_category_data)
    lifestyle_category = lifestyle_category_response.json

    # Create posts with different authors, categories, and statuses
    posts_data = [
        {"title": "Tech Post 1", "author_id": author1["id"], "category_id": tech_category["id"], "status": "published"},
        {"title": "Tech Post 2", "author_id": author2["id"], "category_id": tech_category["id"], "status": "draft"},
        {
            "title": "Lifestyle Post 1",
            "author_id": author1["id"],
            "category_id": lifestyle_category["id"],
            "status": "published",
        },
        {
            "title": "Lifestyle Post 2",
            "author_id": author2["id"],
            "category_id": lifestyle_category["id"],
            "status": "published",
        },
    ]

    created_posts = []
    for post_data in posts_data:
        post_data["content"] = f'Content for {post_data["title"]}'
        post_response = test_blog_app.post_json("/posts", post_data)
        assert post_response.status_code == 200
        created_posts.append(post_response.json)

    # Test filtering by author
    author1_posts_response = test_blog_app.get(f'/posts?author_id={author1["id"]}')
    assert author1_posts_response.status_code == 200
    author1_posts = author1_posts_response.json["posts"]

    for post in author1_posts:
        assert post["author"]["id"] == author1["id"]

    # Test filtering by category
    tech_posts_response = test_blog_app.get(f'/posts?category_id={tech_category["id"]}')
    assert tech_posts_response.status_code == 200
    tech_posts = tech_posts_response.json["posts"]

    for post in tech_posts:
        if post["category"]:  # Some posts might not have categories
            assert post["category"]["id"] == tech_category["id"]

    # Test filtering by status
    published_posts_response = test_blog_app.get("/posts?status=published")
    assert published_posts_response.status_code == 200
    published_posts = published_posts_response.json["posts"]

    for post in published_posts:
        assert post["status"] == "published"

    # Test combined filtering
    author1_tech_response = test_blog_app.get(f'/posts?author_id={author1["id"]}&category_id={tech_category["id"]}')
    assert author1_tech_response.status_code == 200
    author1_tech_posts = author1_tech_response.json["posts"]

    for post in author1_tech_posts:
        assert post["author"]["id"] == author1["id"]
        if post["category"]:
            assert post["category"]["id"] == tech_category["id"]


def test_error_handling_workflow(test_blog_app):
    """Test error handling across the API."""

    # Test 404 errors
    not_found_endpoints = ["/users/999", "/posts/999", "/categories/999", "/comments/999", "/posts/999/comments"]

    for endpoint in not_found_endpoints:
        response = test_blog_app.get(endpoint, expect_errors=True)
        assert response.status_code == 404
        assert "error" in response.json

    # Test 400 errors (bad requests)
    # Invalid status
    response = test_blog_app.get("/posts?status=invalid_status", expect_errors=True)
    assert response.status_code == 400
    assert "Invalid status" in response.json["error"]

    # Create post with invalid author
    invalid_post_data = {"title": "Test Post", "content": "Test content", "author_id": 999}  # Non-existent
    response = test_blog_app.post_json("/posts", invalid_post_data, expect_errors=True)
    assert response.status_code == 400
    assert "Author not found" in response.json["error"]

    # Create comment with invalid author
    # First create a valid post
    author_data = {"username": "test_author", "email": "test@test.com", "full_name": "Test Author"}
    author_response = test_blog_app.post_json("/users", author_data)
    author = author_response.json

    post_data = {"title": "Test Post", "content": "Test content", "author_id": author["id"]}
    post_response = test_blog_app.post_json("/posts", post_data)
    post = post_response.json

    # Try to create comment with invalid author
    invalid_comment_data = {"content": "Test comment", "author_id": 999}  # Non-existent
    response = test_blog_app.post_json(f'/posts/{post["id"]}/comments', invalid_comment_data, expect_errors=True)
    assert response.status_code == 400
    assert "Author not found" in response.json["error"]


def test_data_consistency_workflow(test_blog_app):
    """Test data consistency across related entities."""

    # Create entities
    author_data = {"username": "consistency_author", "email": "consistency@test.com", "full_name": "Consistency Author"}
    author_response = test_blog_app.post_json("/users", author_data)
    author = author_response.json

    category_data = {"name": "Consistency Category", "slug": "consistency-cat"}
    category_response = test_blog_app.post_json("/categories", category_data)
    category = category_response.json

    post_data = {
        "title": "Consistency Post",
        "content": "Testing data consistency",
        "author_id": author["id"],
        "category_id": category["id"],
        "status": "published",
    }
    post_response = test_blog_app.post_json("/posts", post_data)
    post = post_response.json

    comment_data = {"content": "Consistency comment", "author_id": author["id"]}
    comment_response = test_blog_app.post_json(f'/posts/{post["id"]}/comments', comment_data)
    comment = comment_response.json

    # Verify relationships are consistent

    # 1. Post author should match user
    post_detail_response = test_blog_app.get(f'/posts/{post["id"]}')
    post_detail = post_detail_response.json
    assert post_detail["author_id"] == author["id"]

    # 2. Post category should match category
    assert post_detail["category_id"] == category["id"]

    # 3. Comment should be linked to correct post and author
    comment_detail_response = test_blog_app.get(f'/comments/{comment["id"]}')
    comment_detail = comment_detail_response.json
    assert comment_detail["post_id"] == post["id"]
    assert comment_detail["author_id"] == author["id"]
    assert comment_detail["author"]["id"] == author["id"]

    # 4. Category post count should be updated
    category_detail_response = test_blog_app.get(f'/categories/{category["id"]}')
    category_detail = category_detail_response.json
    assert category_detail["post_count"] >= 1

    # 5. User posts should include our post
    user_posts_response = test_blog_app.get(f'/users/{author["id"]}/posts')
    user_posts = user_posts_response.json["posts"]
    user_post_ids = [p["id"] for p in user_posts]
    assert post["id"] in user_post_ids

    # 6. Post comments should include our comment
    post_comments_response = test_blog_app.get(f'/posts/{post["id"]}/comments')
    post_comments = post_comments_response.json
    post_comment_ids = [c["id"] for c in post_comments]
    assert comment["id"] in post_comment_ids
