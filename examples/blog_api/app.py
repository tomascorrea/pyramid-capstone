"""
Pyramid application configuration for the Blog API example.

This demonstrates how to set up a Pyramid application that uses
pyramid-capstone for automatic API endpoint registration.
"""

from pyramid.config import Configurator


def create_app(global_config, data_store_factory=None, **settings):
    """Create and configure the Pyramid application."""
    # Set up data store factory if provided
    if data_store_factory:
        import examples.blog_api.data_store
        import examples.blog_api.views

        # Replace the global data store with the factory-created one
        examples.blog_api.data_store.blog_store = data_store_factory()
        examples.blog_api.views.blog_store = examples.blog_api.data_store.blog_store

    # Create Pyramid configurator
    config = Configurator(settings=settings)

    # Include Cornice for REST API support
    config.include("cornice")

    # Include our pyramid-capstone library (which includes pycornmarsh automatically)
    config.include("pyramid_capstone")
    
    # Enable automatic OpenAPI documentation
    config.capstone_enable_openapi_docs(
        title="Blog API",
        version="1.0.0",
        description="A comprehensive Blog API built with pyramid-capstone demonstrating "
                    "type-hinted endpoints with automatic validation and OpenAPI documentation.",
        api_version="v1"
    )

    # Scan for pyramid-capstone decorated views
    config.scan("examples.blog_api.views", categories=["pyramid_type_hinted"])

    # Add a simple root view for testing
    config.add_route("root", "/")
    config.add_view(root_view, route_name="root", renderer="json")

    # Create and return the WSGI application
    return config.make_wsgi_app()


def root_view(request):
    """Simple root endpoint that provides API information."""
    return {
        "message": "Welcome to the Blog API Example",
        "description": "A comprehensive demonstration of pyramid-capstone with automatic OpenAPI documentation",
        "version": "1.0.0",
        "documentation": {
            "api_explorer": "/api/v1/api-explorer",
            "openapi_json": "/api/v1/openapi.json"
        },
        "features_demonstrated": [
            "Type-hinted API endpoints with automatic validation",
            "CRUD operations for multiple entities (users, posts, categories, comments)",
            "Complex return types (nested objects, lists)",
            "Query parameter handling (pagination, filtering)",
            "Optional parameters with defaults",
            "Error handling with proper HTTP status codes",
            "Automatic OpenAPI documentation generation",
            "Real-world API patterns and relationships",
        ],
        "quick_links": {"health_check": "/health", "blog_statistics": "/stats"},
    }
