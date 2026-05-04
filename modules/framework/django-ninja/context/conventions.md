# Django Ninja: Coding Conventions

## Naming
| Entity | Convention | Example |
|--------|-----------|---------|
| API Instance | `PascalCase` or `api` | `api = NinjaAPI()`, `UserAPI` |
| Routers | `camelCase` or `snake_case` | `userRouter`, `orders_router` |
| Schemas (Input) | `<Model>In` | `UserIn`, `OrderIn` |
| Schemas (Output) | `<Model>Out` | `UserOut`, `OrderOut` |
| Endpoints | `snake_case` | `get_user`, `create_order` |

## File Organization
- **api.py:** Place feature-specific routers in an `api.py` file within each Django app.
- **schemas.py:** Define Pydantic schemas in a `schemas.py` file within each Django app.
- **urls.py:** Mount all app-specific routers in the project's root `urls.py`.

## Documentation
- **OpenAPI:** Provide `summary`, `description`, and `tags` for all endpoints to ensure high-quality documentation.
- **Examples:** Use Pydantic's `Field(examples=[...])` to provide realistic examples for schema fields.
