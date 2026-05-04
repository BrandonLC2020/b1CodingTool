# FastAPI: Best Practices

## Routers & Route Design
- Split routes into **APIRouter** instances, one per resource. Mount all routers in a central `main.py` — never define routes directly on the `FastAPI()` app instance.
- Use meaningful HTTP methods: `GET` for reads, `POST` for creates, `PUT`/`PATCH` for updates, `DELETE` for deletes. Don't use `POST` for everything.
- Version your API from day one: prefix routers with `/api/v1/`.
- Return the correct HTTP status code: `201` for creates, `204` for deletes with no body, `422` is automatic for validation errors.

```python
# Good
router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    return await user_service.create(db, payload)
```

## Dependency Injection
- Use `Depends()` for everything that crosses request boundaries: database sessions, authenticated users, pagination params, feature flags.
- Define the DB session as a generator dependency so SQLAlchemy sessions are always closed on teardown — even on errors.
- Chain dependencies: an `get_current_user` dependency can itself depend on `get_db`, forming a clean hierarchy.

```python
# core/dependencies.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await auth_service.verify_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
```

## SQLAlchemy 2.x Async
- Always use `async with async_session_factory() as session:` — never the sync `Session`.
- Use the 2.x `select()` construct, not the legacy `.query()` ORM API.
- Use `session.execute(select(Model).where(...))` and call `.scalars().all()` or `.scalar_one_or_none()` on the result.
- Use `session.scalar(select(Model)...)` for single-row fetches — it's more concise than `.execute(...).scalar_one()`.
- Wrap multi-step writes in a single transaction: commit once at the end (or let the session dependency handle it).

```python
# Good — SQLAlchemy 2.x style
async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

# Bad — legacy 1.x style
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
```

## Pydantic v2 Schemas
- Use Pydantic models as request/response schemas — never pass raw dicts across the API boundary.
- Separate schemas by intent: `UserCreate` (input), `UserResponse` (output), `UserUpdate` (partial input). Don't reuse one schema for all three.
- Use `model_config = ConfigDict(from_attributes=True)` on response schemas so they can be constructed directly from ORM objects.
- Use `model_validator` and `field_validator` for cross-field validation instead of custom logic in route handlers.

```python
from pydantic import BaseModel, ConfigDict, EmailStr

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
```

## Error Handling
- Raise `HTTPException` for expected, client-facing errors (404, 403, 409). Include a descriptive `detail` string.
- Register a global exception handler for unexpected errors — log the full traceback and return a generic `500` response. Never leak stack traces to clients.
- Use custom exception classes for domain errors; catch them in a middleware or exception handler and convert to `HTTPException`.

```python
@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})
```

## Security
- Never store secrets in source code — use environment variables loaded via `pydantic-settings`.
- Hash passwords with **bcrypt** via `passlib`. Never store plaintext passwords.
- Set `CORS` origins explicitly — never use `allow_origins=["*"]` in production.
- Use `HTTPBearer` or `OAuth2PasswordBearer` for auth token extraction; validate JWTs with `python-jose` or `PyJWT`.

## Background Tasks & Async
- Use FastAPI's `BackgroundTasks` for fire-and-forget work that doesn't need a result (sending emails, webhooks).
- For heavy or long-running work, use a task queue (Celery, ARQ, or Dramatiq) — don't block the event loop.
- Never mix sync and async code without care: calling a blocking I/O function inside an `async def` route will block the entire event loop. Use `run_in_executor` or make the dependency sync.

## Testing
- Use `pytest` with `pytest-asyncio` for async test functions.
- Use `httpx.AsyncClient` with `ASGITransport` for integration tests — it runs the full ASGI stack without a real server.
- Use a dedicated test database and roll back each test in a transaction to keep tests isolated.
- Mock external services at the HTTP boundary (httpx transport), not deep in service functions.

```python
import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/v1/users/", json={"email": "a@b.com", "password": "secret"})
    assert response.status_code == 201
    assert response.json()["email"] == "a@b.com"
```
