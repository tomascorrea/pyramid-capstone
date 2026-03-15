# OpenAPI Documentation (pycornmarsh)

pyramid-capstone automatically generates OpenAPI 3.0 documentation from type hints using pycornmarsh, a Cornice-to-OpenAPI bridge.

## Design Decisions

### pycornmarsh as the OpenAPI Engine

Rather than building a custom OpenAPI generator, the library piggybacks on pycornmarsh which already knows how to extract OpenAPI specs from Cornice services. Since pyramid-capstone generates Cornice services internally, adding pycornmarsh predicates to those services gives OpenAPI generation "for free."

### Opt-in via Config Directive

OpenAPI docs are not enabled by default. Users must call:

```python
config.capstone_enable_openapi_docs(
    title="My API",
    version="1.0.0",
    description="Optional description",
)
```

This registers two routes:
- `{api_prefix}/{api_version}/openapi.json` -- the spec
- `{api_prefix}/{api_version}/api-explorer` -- Swagger UI

Default prefix is `/api`, default version is `v1`.

### Schema Reuse for Request and Response

The same Marshmallow schemas generated for validation (input) and serialization (output) are passed to pycornmarsh as `pcm_request` and `pcm_responses` predicates. No separate OpenAPI schema definitions are needed.

## API Surface

### `capstone_enable_openapi_docs` directive

```python
def capstone_enable_openapi_docs(
    config,
    title: str,
    version: str,
    description: str = None,
    api_version: str = "v1",
    api_prefix: str = "/api",
    security_scheme=None,
) -> None
```

### pycornmarsh predicates (set per view in `service_builder.py`)

`_build_pycornmarsh_predicates()` returns a dict with:
- `pcm_request`: `{"body": input_schema}` (always body, even for GET)
- `pcm_responses`: `{"200": output_schema}` or `{"200": item_schema(many=True)}` for lists
- `pcm_summary`: first line of the handler's docstring
- `pcm_description`: full docstring
- `pcm_tags`: from `tags` kwarg on the decorator
- `pcm_show`: API version string, defaults to `"v1"`

### `includeme` integration

`includeme()` calls `config.include("pycornmarsh")` and registers the directive. pycornmarsh is always included even if the user never calls `capstone_enable_openapi_docs`.

## Key Learnings / Gotchas

- **Input schema always placed under `body`**: `pcm_request={"body": input_schema}` is used even for GET requests. pycornmarsh may render these as request body parameters in the spec rather than query parameters. This is a known simplification.
- **Double-slash workaround**: `capstone_enable_openapi_docs` includes a fix for double slashes in paths that pycornmarsh sometimes produces. It also strips trailing slashes.
- **Version injection**: The spec view injects `api_version` into `request.matchdict["version"]` if missing, because pycornmarsh filters endpoints by version.
- **`ListSchemaInfo` handling**: For `List[ComplexType]` responses, the predicate builder instantiates the item schema with `many=True` to produce the correct array-of-objects representation in OpenAPI.
- **Docstring-driven summaries**: If the decorated function has a docstring, its first line becomes the OpenAPI operation summary. No docstring means no summary in the spec.
