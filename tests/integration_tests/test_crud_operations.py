"""
Integration tests for CRUD operations.

Tests a complete CRUD API with proper path design to avoid routing conflicts.
"""
from dataclasses import dataclass
from typing import List, Optional

from pyramid_capstone import th_api


@dataclass
class Article:
    """Article model for CRUD operations."""

    id: int
    title: str
    content: str
    author: str
    published: bool = False


@dataclass
class CreateArticleRequest:
    """Request model for creating articles."""

    title: str
    content: str
    author: str


@dataclass
class UpdateArticleRequest:
    """Request model for updating articles."""

    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None


# CREATE - POST /crud/create-article
@th_api.post("/crud/create-article")
def create_article(request, title: str, content: str, author: str) -> Article:
    """Create a new article."""
    return Article(id=999, title=title, content=content, author=author, published=False)  # Mock ID


# READ - GET /crud/get-article/{article_id}
@th_api.get("/crud/get-article/{article_id}")
def get_article(request, article_id: int) -> Article:
    """Get an article by ID."""
    return Article(
        id=article_id,
        title=f"Article {article_id}",
        content=f"Content for article {article_id}",
        author="Test Author",
        published=True,
    )


# READ - GET /crud/list-articles
@th_api.get("/crud/list-articles")
def list_articles(request, page: int = 1, limit: int = 10, published_only: bool = False) -> List[Article]:
    """List articles with pagination and filtering."""
    # Mock data
    articles = [
        Article(id=1, title="First Article", content="Content 1", author="Author A", published=True),
        Article(id=2, title="Second Article", content="Content 2", author="Author B", published=False),
        Article(id=3, title="Third Article", content="Content 3", author="Author A", published=True),
    ]

    # Apply filtering
    if published_only:
        articles = [a for a in articles if a.published]

    # Apply pagination (simplified)
    start = (page - 1) * limit
    end = start + limit
    return articles[start:end]


# UPDATE - PUT /crud/update-article/{article_id}
@th_api.put("/crud/update-article/{article_id}")
def update_article(request, article_id: int, title: str, content: str, published: bool = False) -> Article:
    """Update an article."""
    return Article(
        id=article_id, title=title, content=content, author="Updated Author", published=published  # Mock author
    )


# DELETE - DELETE /crud/delete-article/{article_id}
@th_api.delete("/crud/delete-article/{article_id}")
def delete_article(request, article_id: int) -> dict:
    """Delete an article."""
    return {"deleted": True, "article_id": article_id, "message": f"Article {article_id} deleted"}


def test_create_article(app_factory):
    """Test creating a new article."""
    app = app_factory(scan_packages=[__name__])

    article_data = {"title": "New Article", "content": "This is the content of the new article.", "author": "John Doe"}

    response = app.post_json("/crud/create-article", article_data)

    assert response.status_code == 200
    data = response.json
    assert data["id"] == 999
    assert data["title"] == "New Article"
    assert data["content"] == "This is the content of the new article."
    assert data["author"] == "John Doe"
    assert data["published"] is False


def test_get_article(app_factory):
    """Test getting an article by ID."""
    app = app_factory(scan_packages=[__name__])

    response = app.get("/crud/get-article/42")

    assert response.status_code == 200
    data = response.json
    assert data["id"] == 42
    assert data["title"] == "Article 42"
    assert data["content"] == "Content for article 42"
    assert data["author"] == "Test Author"
    assert data["published"] is True


def test_list_articles_default(app_factory):
    """Test listing articles with default parameters."""
    app = app_factory(scan_packages=[__name__])

    response = app.get("/crud/list-articles")

    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) == 3  # All mock articles
    assert data[0]["id"] == 1
    assert data[0]["title"] == "First Article"


def test_list_articles_with_pagination(app_factory):
    """Test listing articles with pagination."""
    app = app_factory(scan_packages=[__name__])

    response = app.get("/crud/list-articles?page=1&limit=2")

    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) == 2  # Limited by pagination
    assert data[0]["id"] == 1
    assert data[1]["id"] == 2


def test_list_articles_published_only(app_factory):
    """Test listing only published articles."""
    app = app_factory(scan_packages=[__name__])

    response = app.get("/crud/list-articles?published_only=true")

    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    assert len(data) == 2  # Only published articles
    assert all(article["published"] for article in data)


def test_update_article(app_factory):
    """Test updating an article."""
    app = app_factory(scan_packages=[__name__])

    update_data = {"title": "Updated Title", "content": "Updated content for the article.", "published": True}

    response = app.put_json("/crud/update-article/123", update_data)

    assert response.status_code == 200
    data = response.json
    assert data["id"] == 123
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content for the article."
    assert data["author"] == "Updated Author"
    assert data["published"] is True


def test_delete_article(app_factory):
    """Test deleting an article."""
    app = app_factory(scan_packages=[__name__])

    response = app.delete("/crud/delete-article/456")

    assert response.status_code == 200
    data = response.json
    assert data["deleted"] is True
    assert data["article_id"] == 456
    assert "Article 456 deleted" in data["message"]


def test_crud_workflow(app_factory):
    """Test a complete CRUD workflow."""
    app = app_factory(scan_packages=[__name__])

    # 1. Create an article
    create_data = {"title": "Workflow Article", "content": "Content for workflow testing.", "author": "Workflow Tester"}
    create_response = app.post_json("/crud/create-article", create_data)
    assert create_response.status_code == 200
    created_article = create_response.json
    assert created_article["title"] == "Workflow Article"

    # 2. Read the article (using mock ID since we can't use the created ID)
    read_response = app.get("/crud/get-article/999")
    assert read_response.status_code == 200

    # 3. Update the article
    update_data = {"title": "Updated Workflow Article", "content": "Updated content.", "published": True}
    update_response = app.put_json("/crud/update-article/999", update_data)
    assert update_response.status_code == 200
    updated_article = update_response.json
    assert updated_article["title"] == "Updated Workflow Article"
    assert updated_article["published"] is True

    # 4. Delete the article
    delete_response = app.delete("/crud/delete-article/999")
    assert delete_response.status_code == 200
    delete_result = delete_response.json
    assert delete_result["deleted"] is True
