"""
Example tests showing how to use the route fixtures.
"""

import pytest


@pytest.mark.parametrize("route_name", [
    'service_users',
    'service_users_user_id'
])
def test_user_route_exists(route_names, route_name):
    """Test that specific user service routes exist."""
    assert route_name in route_names


@pytest.mark.parametrize("route_name,expected_pattern", [
    ('service_users', '/users'),
    ('service_users_user_id', '/users/{user_id}')
])
def test_user_route_patterns(route_patterns, route_name, expected_pattern):
    """Test that user service routes have correct patterns."""
    assert route_patterns[route_name] == expected_pattern


def test_api_endpoints_coverage(route_names):
    """Test that we have good API endpoint coverage."""
    # Count different types of services
    service_routes = [name for name in route_names if name.startswith('service_')]
    
    # We should have a good number of service routes
    assert len(service_routes) >= 8, f"Should have at least 8 service routes, got {len(service_routes)}"


def test_core_services_exist(route_names):
    """Test that core services exist."""
    core_services = ['service_users', 'service_posts', 'service_categories', 'service_health']
    for service in core_services:
        assert service in route_names, f"Core service '{service}' should exist"


def test_path_parameters_consistency(route_patterns):
    """Test that path parameters are consistent across related routes."""
    # User routes should use {user_id}
    user_routes_with_id = {name: pattern for name, pattern in route_patterns.items() 
                          if 'user' in name and '{' in pattern}
    
    for name, pattern in user_routes_with_id.items():
        if '{user_id}' in pattern:
            assert pattern.count('{user_id}') == 1, f"Route '{name}' should have exactly one user_id parameter"
    
    # Post routes should use {post_id}
    post_routes_with_id = {name: pattern for name, pattern in route_patterns.items() 
                          if 'post' in name and '{' in pattern and 'user' not in name}
    
    for name, pattern in post_routes_with_id.items():
        if '{post_id}' in pattern:
            assert pattern.count('{post_id}') == 1, f"Route '{name}' should have exactly one post_id parameter"
