"""
Simple in-memory data store for the Blog API example.

This provides a basic database-like interface for demonstration purposes.
In a real application, you would use SQLAlchemy, MongoDB, or another database.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from .models import User, Category, Post, Comment, PostStatus, PostSummary


class BlogDataStore:
    """In-memory data store for blog entities."""
    
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.categories: Dict[int, Category] = {}
        self.posts: Dict[int, Post] = {}
        self.comments: Dict[int, Comment] = {}
        
        # Auto-increment counters
        self._user_id_counter = 1
        self._category_id_counter = 1
        self._post_id_counter = 1
        self._comment_id_counter = 1
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Create some sample data for demonstration."""
        # Sample users
        self.create_user("john_doe", "john@example.com", "John Doe", "Tech enthusiast and blogger")
        self.create_user("jane_smith", "jane@example.com", "Jane Smith", "Python developer and writer")
        self.create_user("bob_wilson", "bob@example.com", "Bob Wilson")
        
        # Sample categories
        self.create_category("Technology", "technology", "Posts about technology and programming")
        self.create_category("Python", "python", "Python programming tutorials and tips")
        self.create_category("Web Development", "web-dev", "Web development tutorials and best practices")
        
        # Sample posts
        post1_id = self.create_post(
            title="Getting Started with Pyramid",
            content="Pyramid is a powerful Python web framework...",
            excerpt="Learn the basics of Pyramid web framework",
            author_id=1,
            category_id=2,
            status=PostStatus.PUBLISHED
        )
        
        post2_id = self.create_post(
            title="Type Hints in Python",
            content="Type hints make Python code more readable and maintainable...",
            excerpt="Understanding Python type hints and their benefits",
            author_id=2,
            category_id=2,
            status=PostStatus.PUBLISHED
        )
        
        post3_id = self.create_post(
            title="Building REST APIs",
            content="REST APIs are the backbone of modern web applications...",
            excerpt="Best practices for building REST APIs",
            author_id=1,
            category_id=3,
            status=PostStatus.DRAFT
        )
        
        # Sample comments
        self.create_comment(post1_id, 2, "Great introduction to Pyramid! Very helpful.")
        self.create_comment(post1_id, 3, "Thanks for sharing this. Looking forward to more posts.")
        self.create_comment(post2_id, 1, "Type hints have really improved my Python code quality.")
    
    # User operations
    def create_user(self, username: str, email: str, full_name: str, bio: Optional[str] = None) -> int:
        """Create a new user and return the ID."""
        user_id = self._user_id_counter
        self._user_id_counter += 1
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            full_name=full_name,
            bio=bio,
            created_at=datetime.now()
        )
        self.users[user_id] = user
        return user_id
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return self.users.get(user_id)
    
    def get_all_users(self) -> List[User]:
        """Get all users."""
        return list(self.users.values())
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update a user and return the updated user."""
        user = self.users.get(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False
    
    # Category operations
    def create_category(self, name: str, slug: str, description: Optional[str] = None) -> int:
        """Create a new category and return the ID."""
        category_id = self._category_id_counter
        self._category_id_counter += 1
        
        category = Category(
            id=category_id,
            name=name,
            slug=slug,
            description=description
        )
        self.categories[category_id] = category
        return category_id
    
    def get_category(self, category_id: int) -> Optional[Category]:
        """Get a category by ID."""
        return self.categories.get(category_id)
    
    def get_all_categories(self) -> List[Category]:
        """Get all categories."""
        return list(self.categories.values())
    
    # Post operations
    def create_post(self, title: str, content: str, author_id: int, 
                   excerpt: Optional[str] = None, category_id: Optional[int] = None,
                   status: PostStatus = PostStatus.DRAFT) -> int:
        """Create a new post and return the ID."""
        post_id = self._post_id_counter
        self._post_id_counter += 1
        
        # Generate slug from title (simplified)
        slug = title.lower().replace(" ", "-").replace(",", "").replace(".", "")
        
        now = datetime.now()
        post = Post(
            id=post_id,
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt,
            author_id=author_id,
            category_id=category_id,
            status=status,
            created_at=now,
            updated_at=now,
            published_at=now if status == PostStatus.PUBLISHED else None
        )
        self.posts[post_id] = post
        
        # Update category post count
        if category_id and category_id in self.categories:
            self.categories[category_id].post_count += 1
        
        return post_id
    
    def get_post(self, post_id: int, include_relations: bool = False) -> Optional[Post]:
        """Get a post by ID, optionally including related data."""
        post = self.posts.get(post_id)
        if not post:
            return None
        
        if include_relations:
            # Add author information
            post.author = self.get_user(post.author_id)
            
            # Add category information
            if post.category_id:
                post.category = self.get_category(post.category_id)
            
            # Add comments
            post.comments = [c for c in self.comments.values() if c.post_id == post_id]
            for comment in post.comments:
                comment.author = self.get_user(comment.author_id)
        
        return post
    
    def get_posts(self, status: Optional[PostStatus] = None, category_id: Optional[int] = None,
                  author_id: Optional[int] = None, limit: int = 10, offset: int = 0) -> List[PostSummary]:
        """Get posts with filtering and pagination."""
        posts = list(self.posts.values())
        
        # Apply filters
        if status:
            posts = [p for p in posts if p.status == status]
        if category_id:
            posts = [p for p in posts if p.category_id == category_id]
        if author_id:
            posts = [p for p in posts if p.author_id == author_id]
        
        # Sort by creation date (newest first)
        posts.sort(key=lambda p: p.created_at or datetime.min, reverse=True)
        
        # Apply pagination
        paginated_posts = posts[offset:offset + limit]
        
        # Convert to PostSummary with relations
        summaries = []
        for post in paginated_posts:
            # Count comments for this post
            comment_count = len([c for c in self.comments.values() if c.post_id == post.id])
            
            summary = PostSummary(
                id=post.id,
                title=post.title,
                slug=post.slug,
                excerpt=post.excerpt,
                author=self.get_user(post.author_id),
                category=self.get_category(post.category_id) if post.category_id else None,
                status=post.status,
                created_at=post.created_at,
                view_count=post.view_count,
                comment_count=comment_count
            )
            summaries.append(summary)
        
        return summaries
    
    def get_posts_count(self, status: Optional[PostStatus] = None, 
                       category_id: Optional[int] = None, author_id: Optional[int] = None) -> int:
        """Get total count of posts matching filters."""
        posts = list(self.posts.values())
        
        if status:
            posts = [p for p in posts if p.status == status]
        if category_id:
            posts = [p for p in posts if p.category_id == category_id]
        if author_id:
            posts = [p for p in posts if p.author_id == author_id]
        
        return len(posts)
    
    def update_post(self, post_id: int, **kwargs) -> Optional[Post]:
        """Update a post and return the updated post."""
        post = self.posts.get(post_id)
        if not post:
            return None
        
        for key, value in kwargs.items():
            if hasattr(post, key) and value is not None:
                setattr(post, key, value)
        
        post.updated_at = datetime.now()
        
        # Update published_at if status changed to published
        if kwargs.get('status') == PostStatus.PUBLISHED and not post.published_at:
            post.published_at = datetime.now()
        
        return post
    
    def delete_post(self, post_id: int) -> bool:
        """Delete a post."""
        if post_id in self.posts:
            post = self.posts[post_id]
            
            # Update category post count
            if post.category_id and post.category_id in self.categories:
                self.categories[post.category_id].post_count -= 1
            
            # Delete associated comments
            comment_ids_to_delete = [c.id for c in self.comments.values() if c.post_id == post_id]
            for comment_id in comment_ids_to_delete:
                del self.comments[comment_id]
            
            del self.posts[post_id]
            return True
        return False
    
    # Comment operations
    def create_comment(self, post_id: int, author_id: int, content: str) -> int:
        """Create a new comment and return the ID."""
        comment_id = self._comment_id_counter
        self._comment_id_counter += 1
        
        comment = Comment(
            id=comment_id,
            post_id=post_id,
            author_id=author_id,
            content=content,
            created_at=datetime.now()
        )
        self.comments[comment_id] = comment
        return comment_id
    
    def get_comment(self, comment_id: int) -> Optional[Comment]:
        """Get a comment by ID."""
        comment = self.comments.get(comment_id)
        if comment:
            comment.author = self.get_user(comment.author_id)
        return comment
    
    def get_comments_for_post(self, post_id: int) -> List[Comment]:
        """Get all comments for a post."""
        comments = [c for c in self.comments.values() if c.post_id == post_id]
        for comment in comments:
            comment.author = self.get_user(comment.author_id)
        return comments
    
    def delete_comment(self, comment_id: int) -> bool:
        """Delete a comment."""
        if comment_id in self.comments:
            del self.comments[comment_id]
            return True
        return False


# Global data store instance
blog_store = BlogDataStore()
