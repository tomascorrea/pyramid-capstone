"""
Pyramid Capstone

A FastAPI-like decorator system for Pyramid that automatically handles
validation and serialization using Marshmallow schemas and Cornice services.

Usage:
    from pyramid_capstone import th_api
    
    @th_api.get('/users/{user_id}')
    def get_user(request, user_id: int) -> UserResponse:
        return UserResponse(id=user_id, name="John")
"""

from .decorators import th_api
from .exceptions import (
    ParameterConflictError,
    ParameterMissingError,
    SchemaGenerationError,
    ServiceRegistrationError,
    TypeHintedAPIError,
)

__version__ = "0.0.1"


def includeme(config):
    """
    Pyramid includeme function for pyramid-capstone.

    This function is called when the library is included via config.include().
    It sets up any necessary configuration for the library.
    """
    # Ensure Cornice is included
    config.include("cornice")

    # Add any additional configuration here if needed
    # For now, the library works through venusian scanning, so no additional setup is required


__all__ = [
    "th_api",
    "TypeHintedAPIError",
    "ParameterConflictError",
    "ParameterMissingError",
    "SchemaGenerationError",
    "ServiceRegistrationError",
    "includeme",
]
