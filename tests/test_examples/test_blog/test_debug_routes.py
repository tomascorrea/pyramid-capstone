"""
Test to verify that all expected routes are registered correctly.
"""


def test_routes_registration(blog_app):
    """Test that all expected routes are registered correctly."""
    # Get the registry from the app
    registry = blog_app.registry

    # Get the routes mapper
    from pyramid.interfaces import IRoutesMapper

    mapper = registry.queryUtility(IRoutesMapper)

    assert mapper is not None, "Routes mapper should be available"

    routes = mapper.get_routes()
    route_names = [route.name for route in routes]
    route_patterns = {route.name: route.pattern for route in routes}

    # Expected api service routes
    expected_routes = [
        "service_users",
        "service_users_user_id",
        "service_users_user_id_posts",
        "service_posts",
        "service_posts_post_id",
        "service_categories",
        "service_categories_category_id",
        "service_comments_comment_id",
        "service_posts_post_id_comments",
        "service_health",
        "service_stats",
        "root",  # Standard Pyramid route
    ]

    # Check that all expected routes are registered
    for expected_route in expected_routes:
        assert expected_route in route_names, f"Route '{expected_route}' should be registered"

    # Check some specific route patterns
    assert route_patterns["service_users"] == "/users"
    assert route_patterns["service_users_user_id"] == "/users/{user_id}"
    assert route_patterns["service_health"] == "/health"
    assert route_patterns["root"] == "/"

    # Verify we have a reasonable number of routes (should be at least our expected routes)
    assert len(routes) >= len(expected_routes), f"Should have at least {len(expected_routes)} routes, got {len(routes)}"
