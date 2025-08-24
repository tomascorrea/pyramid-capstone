"""
Pyramid application configuration for the Blog API example.

This demonstrates how to set up a Pyramid application that uses
pyramid-type-hinted-api for automatic API endpoint registration.
"""

from pyramid.config import Configurator
from pyramid.response import Response


def create_app(global_config, **settings):
    """Create and configure the Pyramid application."""
    # Create Pyramid configurator
    config = Configurator(settings=settings)
    
    # Include Cornice for REST API support
    config.include('cornice')
    
    # Include our pyramid-type-hinted-api library
    config.include('pyramid_type_hinted_api')
    
    # Include pycornmarsh for OpenAPI documentation
    config.include('pycornmarsh')
    
    # Scan for pyramid-type-hinted-api decorated views
    config.scan('examples.blog_api.views', categories=['pyramid_type_hinted'])
    
    # Add a simple root view for testing
    config.add_route('root', '/')
    config.add_view(root_view, route_name='root', renderer='json')
    
    # Create and return the WSGI application
    return config.make_wsgi_app()


def root_view(request):
    """Simple root endpoint that provides API information."""
    return {
        'message': 'Welcome to the Blog API Example',
        'description': 'A comprehensive demonstration of pyramid-type-hinted-api with automatic OpenAPI documentation',
        'version': '1.0.0',
        'documentation': {
            'swagger_ui': '/swagger-ui/',
            'redoc': '/redoc/',
            'openapi_json': '/openapi.json'
        },
        'features_demonstrated': [
            'Type-hinted API endpoints with automatic validation',
            'CRUD operations for multiple entities (users, posts, categories, comments)',
            'Complex return types (nested objects, lists)',
            'Query parameter handling (pagination, filtering)',
            'Optional parameters with defaults',
            'Error handling with proper HTTP status codes',
            'Automatic OpenAPI documentation generation',
            'Real-world API patterns and relationships'
        ],
        'quick_links': {
            'health_check': '/health',
            'blog_statistics': '/stats'
        }
    }



