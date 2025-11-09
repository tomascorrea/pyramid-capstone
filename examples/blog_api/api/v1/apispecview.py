"""
OpenAPI specification view for Blog API v1.

This module provides the OpenAPI specification for the Blog API endpoints.
"""

from pycornmarsh import get_spec


def api_spec(request):
    """Generate and return the OpenAPI specification for the Blog API."""
    return get_spec(
        request=request,
        title="Blog API",
        version="1.0.0",
        description="A comprehensive Blog API built with pyramid-capstone demonstrating "
                    "type-hinted endpoints with automatic validation and OpenAPI documentation.",
        security_scheme=None,  # Add security scheme here if needed
    )

