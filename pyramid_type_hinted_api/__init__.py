"""
Pyramid Type-Hinted API

A FastAPI-like decorator system for Pyramid that automatically handles
validation and serialization using Marshmallow schemas and Cornice services.

Usage:
    from pyramid_type_hinted_api import th_api
    
    @th_api.get('/users/{user_id}')
    def get_user(request, user_id: int) -> UserResponse:
        return UserResponse(id=user_id, name="John")
"""

from .decorators import th_api
from .exceptions import (
    TypeHintedAPIError,
    ParameterConflictError,
    ParameterMissingError,
    SchemaGenerationError,
    ServiceRegistrationError,
)

__version__ = "0.0.1"

__all__ = [
    "th_api",
    "TypeHintedAPIError",
    "ParameterConflictError", 
    "ParameterMissingError",
    "SchemaGenerationError",
    "ServiceRegistrationError",
]
