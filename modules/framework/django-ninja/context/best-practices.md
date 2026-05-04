# Django Ninja: Best Practices

## API Design
- **Routers over Global API:** Use `NinjaRouter` for feature-specific endpoints and mount them to a main `NinjaAPI` instance in `config/urls.py` or a central `api.py`.
- **Pydantic Schemas:** Always use Pydantic schemas for request and response validation. Avoid using raw dictionaries.
- **Type Safety:** Leverage Python type hints for all endpoint parameters to ensure automatic validation and OpenAPI documentation generation.
- **Error Handling:** Use Django Ninja's built-in exception handlers for common errors (e.g., 404, validation errors).

## Asynchronous Support
- **Async Endpoints:** Use `async def` for endpoints that perform I/O-bound tasks (e.g., network calls) to improve concurrency.
- **Database Access:** When using async endpoints, use `sync_to_async` for Django ORM calls or use an async-compatible database driver.

## Authentication
- **Security Classes:** Use `HttpBearer`, `APIKeyHeader`, or `HttpBasicAuth` for standard authentication patterns.
- **Scoped Auth:** Apply authentication to specific routers or endpoints rather than globally if possible.

## Performance
- **Select/Prefetch Related:** Always use `select_related` and `prefetch_related` in ORM queries to avoid N+1 issues in API responses.
- **Pagination:** Use Django Ninja's pagination support for endpoints that return lists of objects.
