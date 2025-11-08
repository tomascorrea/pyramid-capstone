"""
API endpoints for the Blog API example.

This module demonstrates how to use pyramid-capstone to create
clean, type-safe REST API endpoints with automatic validation and serialization.
"""

from typing import List, Optional

from pyramid_capstone import api

from .data_store import blog_store
from .models import (
    Category,
    Comment,
    Post,
    PostStatus,
    User,
)

# =============================================================================
# Health Check
# =============================================================================


@api.get("/health")
def health_check(request) -> dict:
    """API health check endpoint."""
    return {
        "status": "healthy",
        "service": "blog-api",
        "version": "1.0.0",
        "users_count": len(blog_store.users),
        "posts_count": len(blog_store.posts),
        "categories_count": len(blog_store.categories),
        "comments_count": len(blog_store.comments),
    }


# =============================================================================
# User Management Endpoints
# =============================================================================


@api.get("/users")
def list_users(request) -> List[User]:
    """Get all users."""
    return blog_store.get_all_users()


@api.get("/users/{user_id}")
def get_user(request, user_id: int) -> User:
    """Get a user by ID."""
    user = blog_store.get_user(user_id)
    if not user:
        request.response.status = 404
        return {"error": "User not found"}
    return user


@api.post("/users")
def create_user(request, username: str, email: str, full_name: str, bio: Optional[str] = None) -> User:
    """Create a new user."""
    user_id = blog_store.create_user(username, email, full_name, bio)
    return blog_store.get_user(user_id)


@api.put("/users/{user_id}")
def update_user(
    request, user_id: int, full_name: Optional[str] = None, bio: Optional[str] = None, is_active: Optional[bool] = None
) -> User:
    """Update a user."""
    user = blog_store.update_user(user_id, full_name=full_name, bio=bio, is_active=is_active)
    if not user:
        request.response.status = 404
        return {"error": "User not found"}
    return user


@api.delete("/users/{user_id}")
def delete_user(request, user_id: int) -> dict:
    """Delete a user."""
    if blog_store.delete_user(user_id):
        return {"deleted": True, "user_id": user_id}
    else:
        request.response.status = 404
        return {"error": "User not found"}


# =============================================================================
# Category Management Endpoints
# =============================================================================


@api.get("/categories")
def list_categories(request) -> List[Category]:
    """Get all categories."""
    return blog_store.get_all_categories()


@api.get("/categories/{category_id}")
def get_category(request, category_id: int) -> Category:
    """Get a category by ID."""
    category = blog_store.get_category(category_id)
    if not category:
        request.response.status = 404
        return {"error": "Category not found"}
    return category


@api.post("/categories")
def create_category(request, name: str, slug: str, description: Optional[str] = None) -> Category:
    """Create a new category."""
    category_id = blog_store.create_category(name, slug, description)
    return blog_store.get_category(category_id)


# =============================================================================
# Post Management Endpoints
# =============================================================================


@api.get("/posts")
def list_posts(
    request,
    status: Optional[str] = None,
    category_id: Optional[int] = None,
    author_id: Optional[int] = None,
    page: int = 1,
    per_page: int = 10,
) -> dict:
    """
    Get posts with filtering and pagination.

    Query parameters:
    - status: Filter by post status (draft, published, archived)
    - category_id: Filter by category ID
    - author_id: Filter by author ID
    - page: Page number (default: 1)
    - per_page: Items per page (default: 10, max: 100)
    """
    # Validate and convert status
    post_status = None
    if status:
        try:
            post_status = PostStatus(status)
        except ValueError:
            request.response.status = 400
            return {"error": f"Invalid status. Must be one of: {[s.value for s in PostStatus]}"}

    # Limit per_page to reasonable bounds
    per_page = min(max(per_page, 1), 100)
    offset = (page - 1) * per_page

    # Get posts and total count
    posts = blog_store.get_posts(
        status=post_status, category_id=category_id, author_id=author_id, limit=per_page, offset=offset
    )

    total = blog_store.get_posts_count(status=post_status, category_id=category_id, author_id=author_id)

    pages = (total + per_page - 1) // per_page  # Ceiling division

    return {
        "posts": posts,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1,
        },
    }


@api.get("/posts/{post_id}")
def get_post(request, post_id: int, include_comments: bool = False) -> Post:
    """
    Get a post by ID.

    Query parameters:
    - include_comments: Include comments in the response (default: false)
    """
    post = blog_store.get_post(post_id, include_relations=include_comments)
    if not post:
        request.response.status = 404
        return {"error": "Post not found"}

    # Increment view count
    post.view_count += 1

    return post


@api.post("/posts")
def create_post(
    request,
    title: str,
    content: str,
    author_id: int,
    excerpt: Optional[str] = None,
    category_id: Optional[int] = None,
    status: str = "draft",
) -> Post:
    """Create a new blog post."""
    # Validate status
    try:
        post_status = PostStatus(status)
    except ValueError:
        request.response.status = 400
        return {"error": f"Invalid status. Must be one of: {[s.value for s in PostStatus]}"}

    # Validate author exists
    if not blog_store.get_user(author_id):
        request.response.status = 400
        return {"error": "Author not found"}

    # Validate category exists (if provided)
    if category_id and not blog_store.get_category(category_id):
        request.response.status = 400
        return {"error": "Category not found"}

    post_id = blog_store.create_post(
        title=title, content=content, author_id=author_id, excerpt=excerpt, category_id=category_id, status=post_status
    )

    return blog_store.get_post(post_id, include_relations=True)


@api.put("/posts/{post_id}")
def update_post(
    request,
    post_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    excerpt: Optional[str] = None,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
) -> Post:
    """Update a blog post."""
    # Validate status if provided
    post_status = None
    if status:
        try:
            post_status = PostStatus(status)
        except ValueError:
            request.response.status = 400
            return {"error": f"Invalid status. Must be one of: {[s.value for s in PostStatus]}"}

    # Validate category exists (if provided)
    if category_id and not blog_store.get_category(category_id):
        request.response.status = 400
        return {"error": "Category not found"}

    post = blog_store.update_post(
        post_id, title=title, content=content, excerpt=excerpt, category_id=category_id, status=post_status
    )

    if not post:
        request.response.status = 404
        return {"error": "Post not found"}

    return blog_store.get_post(post_id, include_relations=True)


@api.delete("/posts/{post_id}")
def delete_post(request, post_id: int) -> dict:
    """Delete a blog post."""
    if blog_store.delete_post(post_id):
        return {"deleted": True, "post_id": post_id}
    else:
        request.response.status = 404
        return {"error": "Post not found"}


# =============================================================================
# Comment Management Endpoints
# =============================================================================


@api.get("/posts/{post_id}/comments")
def list_post_comments(request, post_id: int) -> List[Comment]:
    """Get all comments for a post."""
    # Verify post exists
    if not blog_store.get_post(post_id):
        request.response.status = 404
        return {"error": "Post not found"}

    return blog_store.get_comments_for_post(post_id)


@api.post("/posts/{post_id}/comments")
def create_comment(request, post_id: int, content: str, author_id: int) -> Comment:
    """Create a new comment on a post."""
    # Verify post exists
    if not blog_store.get_post(post_id):
        request.response.status = 404
        return {"error": "Post not found"}

    # Verify author exists
    if not blog_store.get_user(author_id):
        request.response.status = 400
        return {"error": "Author not found"}

    comment_id = blog_store.create_comment(post_id, author_id, content)
    return blog_store.get_comment(comment_id)


@api.get("/comments/{comment_id}")
def get_comment(request, comment_id: int) -> Comment:
    """Get a comment by ID."""
    comment = blog_store.get_comment(comment_id)
    if not comment:
        request.response.status = 404
        return {"error": "Comment not found"}
    return comment


@api.delete("/comments/{comment_id}")
def delete_comment(request, comment_id: int) -> dict:
    """Delete a comment."""
    if blog_store.delete_comment(comment_id):
        return {"deleted": True, "comment_id": comment_id}
    else:
        request.response.status = 404
        return {"error": "Comment not found"}


# =============================================================================
# Statistics and Analytics Endpoints
# =============================================================================


@api.get("/stats")
def get_blog_stats(request) -> dict:
    """Get blog statistics."""
    published_posts = blog_store.get_posts_count(status=PostStatus.PUBLISHED)
    draft_posts = blog_store.get_posts_count(status=PostStatus.DRAFT)

    return {
        "users": {"total": len(blog_store.users), "active": len([u for u in blog_store.users.values() if u.is_active])},
        "posts": {
            "total": len(blog_store.posts),
            "published": published_posts,
            "drafts": draft_posts,
            "archived": blog_store.get_posts_count(status=PostStatus.ARCHIVED),
        },
        "categories": {"total": len(blog_store.categories)},
        "comments": {"total": len(blog_store.comments)},
    }


@api.get("/users/{user_id}/posts")
def get_user_posts(request, user_id: int, status: Optional[str] = None, page: int = 1, per_page: int = 10) -> dict:
    """Get posts by a specific user."""
    # Verify user exists
    if not blog_store.get_user(user_id):
        request.response.status = 404
        return {"error": "User not found"}

    # Validate status
    post_status = None
    if status:
        try:
            post_status = PostStatus(status)
        except ValueError:
            request.response.status = 400
            return {"error": f"Invalid status. Must be one of: {[s.value for s in PostStatus]}"}

    per_page = min(max(per_page, 1), 100)
    offset = (page - 1) * per_page

    posts = blog_store.get_posts(status=post_status, author_id=user_id, limit=per_page, offset=offset)

    total = blog_store.get_posts_count(status=post_status, author_id=user_id)
    pages = (total + per_page - 1) // per_page

    return {
        "posts": posts,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
            "has_next": page < pages,
            "has_prev": page > 1,
        },
    }
