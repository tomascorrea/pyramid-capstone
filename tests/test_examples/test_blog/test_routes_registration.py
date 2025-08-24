"""
Test to verify that all expected routes are registered correctly.
"""

import pytest


@pytest.mark.parametrize(
    "expected_route",
    [
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
    ],
)
def test_expected_route_registered(route_names, expected_route):
    """Test that each expected route is registered."""
    assert expected_route in route_names, f"Route '{expected_route}' should be registered"


@pytest.mark.parametrize(
    "route_name,expected_pattern",
    [
        ("service_users", "/users"),
        ("service_users_user_id", "/users/{user_id}"),
        ("service_users_user_id_posts", "/users/{user_id}/posts"),
        ("service_health", "/health"),
        ("root", "/"),
        ("service_posts", "/posts"),
        ("service_posts_post_id", "/posts/{post_id}"),
        ("service_categories", "/categories"),
        ("service_categories_category_id", "/categories/{category_id}"),
        ("service_stats", "/stats"),
        ("service_comments_comment_id", "/comments/{comment_id}"),
        ("service_posts_post_id_comments", "/posts/{post_id}/comments"),
    ],
)
def test_route_pattern_correct(route_patterns, route_name, expected_pattern):
    """Test that specific routes have correct patterns."""
    assert route_patterns[route_name] == expected_pattern


def test_sufficient_routes_registered(route_names):
    """Test that we have a reasonable number of routes registered."""
    expected_minimum = 12  # Updated for new service-based architecture (was 20 with individual method routes)
    assert (
        len(route_names) >= expected_minimum
    ), f"Should have at least {expected_minimum} routes, got {len(route_names)}"
