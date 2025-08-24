"""
Data models for the Blog API example.

These models demonstrate various type hint patterns that work well with
pyramid-type-hinted-api's automatic schema generation.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class PostStatus(str, Enum):
    """Post publication status."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


@dataclass
class User:
    """User model representing blog authors and commenters."""
    id: int
    username: str
    email: str
    full_name: str
    bio: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None


@dataclass
class Category:
    """Category model for organizing blog posts."""
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    post_count: int = 0


@dataclass
class Comment:
    """Comment model for post discussions."""
    id: int
    post_id: int
    author_id: int
    content: str
    created_at: datetime
    author: Optional[User] = None  # Will be populated when needed


@dataclass
class Post:
    """Blog post model with full details."""
    id: int
    title: str
    slug: str
    content: str
    author_id: int
    excerpt: Optional[str] = None
    category_id: Optional[int] = None
    status: PostStatus = PostStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    view_count: int = 0
    # Related objects (populated when needed)
    author: Optional[User] = None
    category: Optional[Category] = None
    comments: List[Comment] = field(default_factory=list)


# Request/Response models for API operations

@dataclass
class CreateUserRequest:
    """Request model for creating a new user."""
    username: str
    email: str
    full_name: str
    bio: Optional[str] = None


@dataclass
class UpdateUserRequest:
    """Request model for updating user information."""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None


@dataclass
class CreateCategoryRequest:
    """Request model for creating a new category."""
    name: str
    slug: str
    description: Optional[str] = None


@dataclass
class CreatePostRequest:
    """Request model for creating a new blog post."""
    title: str
    content: str
    excerpt: Optional[str] = None
    category_id: Optional[int] = None
    status: PostStatus = PostStatus.DRAFT


@dataclass
class UpdatePostRequest:
    """Request model for updating a blog post."""
    title: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    category_id: Optional[int] = None
    status: Optional[PostStatus] = None


@dataclass
class CreateCommentRequest:
    """Request model for creating a new comment."""
    content: str
    author_id: int


@dataclass
class PaginatedResponse:
    """Generic paginated response wrapper."""
    items: List[dict]  # Will contain the actual items
    total: int
    page: int
    per_page: int
    pages: int


@dataclass
class PostSummary:
    """Simplified post model for list views."""
    id: int
    title: str
    slug: str
    excerpt: Optional[str]
    author: User
    category: Optional[Category]
    status: PostStatus
    created_at: Optional[datetime]
    view_count: int
    comment_count: int = 0
