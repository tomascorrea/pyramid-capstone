"""
Pyramid shell setup for the Blog API example.
"""

from .data_store import blog_store


def setup(env):
    """Setup the pshell environment with useful objects."""
    env['blog_store'] = blog_store
    env['users'] = blog_store.users
    env['posts'] = blog_store.posts
    env['categories'] = blog_store.categories
    env['comments'] = blog_store.comments
    
    print("Blog API shell environment loaded!")
    print("Available objects:")
    print("  blog_store - The main data store")
    print("  users      - User data dictionary")
    print("  posts      - Post data dictionary")
    print("  categories - Category data dictionary")
    print("  comments   - Comment data dictionary")
