# FastAPI: Directory Structure

## Recommended Layout

```
project_root/
├── pyproject.toml             # Project metadata, dependencies (uv or Poetry), tool config
├── .env                       # Local secrets — never commit
├── alembic.ini                # Alembic migration config
├── alembic/
│   ├── env.py                 # Alembic async engine setup
│   └── versions/              # Auto-generated migration files
├── app/
│   ├── main.py                # FastAPI() instance, router mounts, lifespan handler
│   ├── core/
│   │   ├── config.py          # pydantic-settings Settings class (single source of truth)
│   │   ├── database.py        # async engine + async_session_factory
│   │   ├── dependencies.py    # Shared Depends: get_db, get_current_user, pagination
│   │   └── security.py        # JWT creation/verification, password hashing
│   ├── features/
│   │   ├── users/
│   │   │   ├── models.py      # SQLAlchemy ORM models
│   │   │   ├── schemas.py     # Pydantic request/response schemas
│   │   │   ├── service.py     # Business logic (async functions, no HTTP concerns)
│   │   │   ├── router.py      # APIRouter — route handlers only, calls service
│   │   │   └── dependencies.py # Feature-local Depends (e.g. get_user_or_404)
│   │   └── posts/
│   │       └── ...            # Same structure as users/
│   └── middleware/            # Custom Starlette middleware (logging, tracing, etc.)
└── tests/
    ├── conftest.py            # Fixtures: test DB, async client, factories
    ├── unit/
    │   └── features/
    │       └── users/
    │           └── test_user_service.py
    └── integration/
        └── features/
            └── users/
                └── test_user_router.py
```

## Application Entrypoint

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import engine, Base
from app.features.users.router import router as users_router
from app.features.posts.router import router as posts_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: run migrations or create tables in dev
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: dispose connection pool
    await engine.dispose()

app = FastAPI(title="My API", version="1.0.0", lifespan=lifespan)

app.include_router(users_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")
```

## Database Setup

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
```

## Feature Module Pattern

Each feature owns its **models**, **schemas**, **service**, and **router**. The router calls the service; the service calls the DB. Nothing skips layers.

```
users/
  models.py   → SQLAlchemy ORM (database shape)
  schemas.py  → Pydantic models (API shape)
  service.py  → async business logic (no HTTP knowledge)
  router.py   → HTTP handlers (no business logic)
```

## Migrations (Alembic)
- Configure Alembic to use the async engine via `run_sync`.
- Always generate migrations with a descriptive name: `alembic revision --autogenerate -m "add_bio_to_users"`.
- Review generated migration files before committing — autogenerate can miss constraints or produce destructive changes.
- Never hand-edit migration files unless resolving a conflict or squash.

## Key Files Reference
| File | Purpose |
|------|---------|
| `app/core/config.py` | Single `Settings` instance — import this everywhere |
| `app/core/database.py` | Engine and session factory |
| `app/core/dependencies.py` | `get_db`, `get_current_user` — used across all features |
| `app/core/security.py` | JWT, bcrypt helpers |
| `tests/conftest.py` | Async test client, DB fixtures, factory setup |
| `alembic/env.py` | Must import all models so autogenerate detects them |
