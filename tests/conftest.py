"""
Pytest configuration and fixtures for pyramid-capstone tests.

This module provides reusable fixtures for testing the type-hinted API system,
including a flexible Pyramid app factory and test client setup.
"""

from typing import Any, Callable, Dict, List, Optional

import pytest
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.security import Allow, Authenticated, Everyone
from pyramid.testing import setUp, tearDown
from webtest import TestApp

from pyramid_capstone import th_api


class StaticAuthenticationPolicy:
    """Simple static authentication policy for testing."""

    def authenticated_userid(self, request):
        # Check for simple Authorization header: "Bearer userid"
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        return None

    def effective_principals(self, request):
        userid = self.authenticated_userid(request)
        if not userid:
            return ["system.Everyone"]

        principals = ["system.Everyone", "system.Authenticated", userid]

        # Add groups based on userid
        user_groups = {
            "user1": [],
            "editor1": ["editors"],
            "admin1": ["admins"],
        }

        if userid in user_groups:
            for group in user_groups[userid]:
                principals.append(f"group:{group}")

        return principals

    def remember(self, request, userid, **kw):
        return []

    def forget(self, request):
        return []


class RootFactory:
    """Root factory with ACL for testing security."""

    __acl__ = [
        (Allow, Everyone, "public"),
        (Allow, Authenticated, "view"),
        (Allow, "group:editors", "edit"),
        (Allow, "group:admins", "edit"),  # Admins can also edit
        (Allow, "group:admins", "admin"),
    ]

    def __init__(self, request):
        pass


@pytest.fixture
def pyramid_config():
    """
    Create a basic Pyramid configurator for testing.

    Provides a consistent base configuration that includes Cornice
    and standard test settings.

    Returns:
        Function that creates Pyramid configurator with optional settings
    """

    def _create_config(settings: Optional[Dict[str, Any]] = None, enable_security: bool = False):
        # Default test settings
        default_settings = {
            "pyramid.debug_authorization": False,
            "pyramid.debug_notfound": False,
            "pyramid.debug_routematch": False,
        }

        # Merge with provided settings
        if settings:
            default_settings.update(settings)

        config = Configurator(settings=default_settings)
        config.include("cornice")

        # Configure security if requested
        if enable_security:
            # Set up security policies
            authn_policy = StaticAuthenticationPolicy()
            authz_policy = ACLAuthorizationPolicy()

            config.set_authentication_policy(authn_policy)
            config.set_authorization_policy(authz_policy)
            config.set_root_factory(RootFactory)

        return config

    return _create_config


@pytest.fixture
def pyramid_app(pyramid_config):
    """
    Create a basic Pyramid WSGI application for testing.

    Uses the pyramid_config fixture to ensure consistent configuration.

    Args:
        pyramid_config: Pyramid configurator factory fixture

    Returns:
        Function that creates Pyramid WSGI application with optional settings
    """

    def _create_app(
        settings: Optional[Dict[str, Any]] = None,
        scan_packages: Optional[List[str]] = None,
        enable_security: bool = False,
    ):
        # Create configurator with settings
        config = pyramid_config(settings, enable_security=enable_security)

        # Include pyramid_capstone
        config.include("pyramid_capstone")

        # Scan packages for decorated views
        scan_packages = scan_packages or ["pyramid_capstone"]
        for package in scan_packages:
            # Scan with our custom venusian category
            config.scan(package, categories=["pyramid_type_hinted"])

        # Create and return the WSGI app
        return config.make_wsgi_app()

    return _create_app


@pytest.fixture
def app_factory(pyramid_app):
    """
    Factory fixture for creating custom Pyramid apps with specific views and settings.

    Uses the existing pyramid_app fixture to ensure consistency.

    Args:
        pyramid_app: The Pyramid app factory fixture

    Returns:
        Function that creates TestApp instances with custom configuration
    """

    def _create_app(
        settings: Optional[Dict[str, Any]] = None,
        scan_packages: Optional[List[str]] = None,
        enable_security: bool = False,
    ) -> TestApp:
        """
        Create a Pyramid app with custom settings and scanning options.

        Args:
            settings: Dictionary of Pyramid settings to use
            scan_packages: List of packages to scan for views
            enable_security: Whether to enable security policies

        Returns:
            WebTest TestApp instance
        """
        # Create WSGI app using pyramid_app factory
        wsgi_app = pyramid_app(settings=settings, scan_packages=scan_packages, enable_security=enable_security)
        return TestApp(wsgi_app)

    return _create_app


@pytest.fixture
def app_request(app_factory):
    """
    Create a real Pyramid request for testing.

    Always creates real Pyramid requests using the app factory, never DummyRequest.
    This ensures consistent behavior and proper Pyramid context.

    Args:
        app_factory: App factory fixture

    Returns:
        Function that creates real Pyramid request objects
    """

    def _create_request(
        path: str = "/",
        method: str = "GET",
        settings: Optional[Dict[str, Any]] = None,
        scan_packages: Optional[List[str]] = None,
        enable_security: bool = False,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **request_kwargs: Any,
    ):
        """
        Create a real Pyramid request.

        Args:
            path: Request path (can include query string)
            method: HTTP method
            settings: Pyramid app settings
            scan_packages: Packages to scan for views
            json: JSON body data
            params: Form parameters
            headers: HTTP headers
            **request_kwargs: Additional request parameters for WebTest

        Returns:
            Real Pyramid request object
        """
        # Create test app
        test_app = app_factory(settings=settings, scan_packages=scan_packages, enable_security=enable_security)

        # Prepare request arguments
        webtest_kwargs = {}
        if json is not None:
            webtest_kwargs["json"] = json
        if params is not None:
            webtest_kwargs["params"] = params
        if headers is not None:
            webtest_kwargs["headers"] = headers
        webtest_kwargs.update(request_kwargs)

        # Create a test request using WebTest, then extract the Pyramid request
        environ = test_app.RequestClass.blank(path, **webtest_kwargs).environ

        # Get the Pyramid app and create a request from the environ
        pyramid_app = test_app.app
        request = pyramid_app.request_factory(environ)

        return request

    return _create_request


@pytest.fixture(autouse=True)
def pyramid_testing_setup_teardown():
    """
    Automatically setup and teardown Pyramid testing environment.

    This fixture runs before and after each test to ensure clean state.
    """
    # Setup
    setUp()

    yield

    # Teardown
    tearDown()


@pytest.fixture
def sample_user_response():
    """
    Sample user response data for testing.

    Returns:
        Dictionary representing a user response
    """
    return {"id": 123, "name": "John Doe", "email": "john@example.com", "active": True}


@pytest.fixture
def sample_user_request():
    """
    Sample user request data for testing.

    Returns:
        Dictionary representing a user creation request
    """
    return {"name": "Jane Smith", "email": "jane@example.com", "age": 25}


@pytest.fixture
def create_test_view():
    """
    Factory fixture for creating test views with type hints.

    Returns:
        Function that creates decorated test views
    """

    def _create_view(path: str, method: str = "GET", return_type: Any = dict, **params: Any) -> Callable:
        """
        Create a test view with specified parameters and return type.

        Args:
            path: URL path pattern
            method: HTTP method
            return_type: Return type annotation
            **params: Parameter name -> type mappings

        Returns:
            Decorated view function
        """
        # Build function signature dynamically
        ["request", *list(params.keys())]
        param_annotations = {"request": Any, "return": return_type}
        param_annotations.update(params)

        # Create the view function
        def test_view(request, **kwargs):
            # Simple test implementation
            result = {"method": method, "path": path}
            result.update(kwargs)
            return result

        # Set annotations
        test_view.__annotations__ = param_annotations
        test_view.__name__ = f"test_view_{method.lower()}_{path.replace('/', '_').replace('{', '').replace('}', '')}"

        # Apply the appropriate decorator
        decorator = getattr(th_api, method.lower())
        return decorator(path)(test_view)

    return _create_view


# Test data fixtures
@pytest.fixture
def valid_user_data():
    """Valid user data for testing."""
    return {"name": "Test User", "email": "test@example.com", "age": 30, "active": True}


@pytest.fixture
def invalid_user_data():
    """Invalid user data for testing validation errors."""
    return {
        "name": "",  # Empty name
        "email": "invalid-email",  # Invalid email format
        "age": "not-a-number",  # Invalid age type
    }


@pytest.fixture
def path_params():
    """Sample path parameters for testing."""
    return {"user_id": "123", "post_id": "456"}


@pytest.fixture
def query_params():
    """Sample query parameters for testing."""
    return {"limit": "10", "offset": "0", "sort": "name"}


@pytest.fixture
def json_body():
    """Sample JSON body for testing."""
    return {"title": "Test Post", "content": "This is a test post content", "tags": ["test", "example"]}
