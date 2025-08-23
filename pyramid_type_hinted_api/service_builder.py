"""
Cornice service builder for type-hinted API views.

This module creates Cornice services dynamically from decorated functions,
handling validation, serialization, and integration with Pyramid.
"""

from typing import Callable, Any, Optional, Type
from pyramid.config import Configurator
from cornice import Service
from marshmallow import Schema
from .inspection import inspect_function_signature
from .context import ParameterContext, validate_path_pattern
from .schema_generator import generate_input_schema, generate_output_schema
from .handler import create_view_handler
from .exceptions import ServiceRegistrationError


def register_type_hinted_view(
    config: Configurator,
    func: Callable,
    method: str,
    path: str,
    **kwargs: Any
) -> None:
    """
    Register a type-hinted view function as a Cornice service.
    
    This is the main integration point called by venusian when scanning
    decorated functions.
    
    Args:
        config: Pyramid configurator
        func: Decorated function to register
        method: HTTP method (GET, POST, etc.)
        path: URL path pattern
        **kwargs: Additional service configuration
    """
    try:
        # Validate path pattern
        validate_path_pattern(path)
        
        # Inspect function signature
        signature = inspect_function_signature(func)
        
        # Create parameter context and validate
        context = ParameterContext(path)
        context.validate_no_conflicts(signature)
        
        # Generate schemas
        input_schema = generate_input_schema(signature, f"{func.__name__}InputSchema")
        output_schema = generate_output_schema(signature.return_type, f"{func.__name__}OutputSchema")
        
        # Create Cornice service
        service = create_cornice_service(
            name=f"{func.__name__}_{method.lower()}",
            path=path,
            method=method,
            **kwargs
        )
        
        # Create view handler
        view_handler = create_view_handler(
            original_func=func,
            signature=signature,
            context=context,
            input_schema=input_schema,
            output_schema=output_schema
        )
        
        # Register the service with the handler
        service.add_view(method, view_handler)
        
        # Add the service to Pyramid configuration
        config.add_cornice_service(service)
        
    except Exception as e:
        raise ServiceRegistrationError(
            f"Failed to register view {func.__name__} for {method} {path}: {e}"
        ) from e


def create_cornice_service(
    name: str,
    path: str,
    method: str,
    **kwargs: Any
) -> Service:
    """
    Create a Cornice service with the specified configuration.
    
    Args:
        name: Service name
        path: URL path pattern
        method: HTTP method
        **kwargs: Additional service configuration
        
    Returns:
        Configured Cornice service
    """
    # Convert path pattern from {param} to Pyramid's {param} format
    # (they're already compatible, but we could add validation here)
    pyramid_path = path
    
    # Create the service
    service = Service(
        name=name,
        path=pyramid_path,
        description=kwargs.get('description', f'{method} {path}'),
        **{k: v for k, v in kwargs.items() if k != 'description'}
    )
    
    return service


def add_validation_to_service(
    service: Service,
    input_schema: Optional[Type[Schema]],
    output_schema: Optional[Type[Schema]]
) -> None:
    """
    Add validation schemas to a Cornice service.
    
    Args:
        service: Cornice service to configure
        input_schema: Schema for request validation
        output_schema: Schema for response validation
    """
    if input_schema:
        # Add request validation
        def validate_request(request, **kwargs):
            """Validate request data using the input schema."""
            try:
                # Extract data based on request method
                if request.method in ('POST', 'PUT', 'PATCH'):
                    # For body methods, validate JSON body
                    if request.content_type == 'application/json':
                        data = request.json_body
                    else:
                        data = dict(request.POST)
                else:
                    # For GET/DELETE, validate query parameters
                    data = dict(request.GET)
                
                # Add path parameters
                if hasattr(request, 'matchdict') and request.matchdict:
                    data.update(request.matchdict)
                
                # Validate using schema
                schema_instance = input_schema()
                validated_data = schema_instance.load(data)
                
                # Store validated data on request for handler to use
                request.validated_data = validated_data
                
            except Exception as e:
                request.errors.add('body', 'validation', str(e))
        
        service.add_validator(validate_request)
    
    if output_schema:
        # Add response validation/serialization
        def serialize_response(request, response):
            """Serialize response data using the output schema."""
            try:
                if hasattr(response, 'json') and response.json:
                    schema_instance = output_schema()
                    serialized_data = schema_instance.dump(response.json)
                    response.json = serialized_data
            except Exception:
                # If serialization fails, let the original response through
                pass
        
        service.add_filter(serialize_response)


def convert_path_to_pyramid_route(path: str) -> str:
    """
    Convert a path pattern to Pyramid route format if needed.
    
    Args:
        path: Path pattern (e.g., '/users/{user_id}')
        
    Returns:
        Pyramid-compatible route pattern
    """
    # For now, the formats are compatible
    # This function exists for future compatibility if needed
    return path


def extract_service_metadata(func: Callable) -> dict:
    """
    Extract metadata from a decorated function for service configuration.
    
    Args:
        func: Decorated function
        
    Returns:
        Dictionary of service metadata
    """
    metadata = {}
    
    # Extract docstring for description
    if func.__doc__:
        metadata['description'] = func.__doc__.strip()
    
    # Extract any custom attributes set by decorators
    for attr_name in dir(func):
        if attr_name.startswith('__th_api_'):
            key = attr_name[9:]  # Remove '__th_api_' prefix
            metadata[key] = getattr(func, attr_name)
    
    return metadata
