"""
Performance benchmarks comparing Capstone views vs plain Cornice services.

Measures the per-request overhead that pyramid-capstone's decorator layer
adds on top of raw Cornice, across three endpoint patterns:

1. Simple GET (dict response, no params)
2. GET with path parameter (int conversion + dataclass serialization)
3. POST with JSON body (input validation + dataclass serialization)

Both implementations go through the full WSGI stack via WebTest.

Run benchmarks:
    poetry run pytest tests/benchmark_tests/ --benchmark-only

Run as regular tests (sanity check):
    poetry run pytest tests/benchmark_tests/ --benchmark-disable
"""

from dataclasses import dataclass

import pytest
from cornice import Service
from pyramid.config import Configurator
from webtest import TestApp

from pyramid_capstone import api


# ---------------------------------------------------------------------------
# Shared data models
# ---------------------------------------------------------------------------

@dataclass
class BenchUser:
    id: int
    name: str
    email: str


# ---------------------------------------------------------------------------
# Capstone views (discovered by Venusian scan of this module)
# ---------------------------------------------------------------------------

@api.get("/capstone/health")
def capstone_health(request) -> dict:
    return {"status": "ok"}


@api.get("/capstone/users/{user_id}")
def capstone_get_user(request, user_id: int) -> BenchUser:
    return BenchUser(id=user_id, name=f"User {user_id}", email=f"user{user_id}@test.com")


@api.post("/capstone/users")
def capstone_create_user(request, name: str, email: str) -> BenchUser:
    return BenchUser(id=1, name=name, email=email)


# ---------------------------------------------------------------------------
# Plain Cornice services (registered manually, no Marshmallow overhead)
# ---------------------------------------------------------------------------

cornice_health_svc = Service(name="cornice_health", path="/cornice/health")
cornice_users_svc = Service(name="cornice_users_item", path="/cornice/users/{user_id}")
cornice_users_create_svc = Service(name="cornice_users_create", path="/cornice/users")


@cornice_health_svc.get()
def cornice_health(request):
    return {"status": "ok"}


@cornice_users_svc.get()
def cornice_get_user(request):
    user_id = int(request.matchdict["user_id"])
    return {"id": user_id, "name": f"User {user_id}", "email": f"user{user_id}@test.com"}


@cornice_users_create_svc.post()
def cornice_create_user(request):
    body = request.json_body
    return {"id": 1, "name": body["name"], "email": body["email"]}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def capstone_app():
    config = Configurator()
    config.include("cornice")
    config.include("pyramid_capstone")
    config.scan(__name__, categories=["pyramid_type_hinted"])
    return TestApp(config.make_wsgi_app())


@pytest.fixture(scope="module")
def cornice_app():
    config = Configurator()
    config.include("cornice")
    config.scan(__name__)
    return TestApp(config.make_wsgi_app())


# ---------------------------------------------------------------------------
# Benchmark: Simple GET
# ---------------------------------------------------------------------------

def test_benchmark_capstone_simple_get(benchmark, capstone_app):
    response = capstone_app.get("/capstone/health")
    assert response.json == {"status": "ok"}

    benchmark(capstone_app.get, "/capstone/health")


def test_benchmark_cornice_simple_get(benchmark, cornice_app):
    response = cornice_app.get("/cornice/health")
    assert response.json == {"status": "ok"}

    benchmark(cornice_app.get, "/cornice/health")


# ---------------------------------------------------------------------------
# Benchmark: GET with path parameter
# ---------------------------------------------------------------------------

def test_benchmark_capstone_get_with_path_param(benchmark, capstone_app):
    response = capstone_app.get("/capstone/users/42")
    assert response.json["id"] == 42
    assert response.json["name"] == "User 42"

    benchmark(capstone_app.get, "/capstone/users/42")


def test_benchmark_cornice_get_with_path_param(benchmark, cornice_app):
    response = cornice_app.get("/cornice/users/42")
    assert response.json["id"] == 42
    assert response.json["name"] == "User 42"

    benchmark(cornice_app.get, "/cornice/users/42")


# ---------------------------------------------------------------------------
# Benchmark: POST with JSON body
# ---------------------------------------------------------------------------

USER_PAYLOAD = {"name": "Jane Doe", "email": "jane@test.com"}


def test_benchmark_capstone_post_with_body(benchmark, capstone_app):
    response = capstone_app.post_json("/capstone/users", USER_PAYLOAD)
    assert response.json["name"] == "Jane Doe"
    assert response.json["email"] == "jane@test.com"

    benchmark(capstone_app.post_json, "/capstone/users", USER_PAYLOAD)


def test_benchmark_cornice_post_with_body(benchmark, cornice_app):
    response = cornice_app.post_json("/cornice/users", USER_PAYLOAD)
    assert response.json["name"] == "Jane Doe"
    assert response.json["email"] == "jane@test.com"

    benchmark(cornice_app.post_json, "/cornice/users", USER_PAYLOAD)
