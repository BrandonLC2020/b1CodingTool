# FastAPI: Coding Conventions

## Python Style
- Follow **PEP 8**. Use **Ruff** for linting and formatting (it replaces Black, isort, and Flake8 in one tool).
- Type-annotate all function signatures. Use `from __future__ import annotations` at the top of every file.
- Use `X | Y` union syntax (Python 3.10+) over `Optional[X]` or `Union[X, Y]`.
- Return type annotations on route handlers must match the `response_model` — FastAPI validates the response against it.

## Import Order (Ruff / isort groups)
1. Standard library
2. FastAPI and Pydantic
3. Third-party packages (SQLAlchemy, etc.)
4. Local app imports

```python
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db
from app.features.users.models import User
```

## Naming
| Entity | Convention | Example |
|--------|-----------|---------|
| Modules / files | `snake_case.py` | `user_service.py`, `auth_router.py` |
| Classes (models, schemas) | `PascalCase` | `User`, `UserCreate`, `UserResponse` |
| Functions / methods | `snake_case` | `get_user_by_email`, `create_access_token` |
| Route handler functions | `<verb>_<resource>` | `create_user`, `get_user`, `delete_post` |
| Pydantic schemas (input) | `<Model>Create` / `<Model>Update` | `UserCreate`, `PostUpdate` |
| Pydantic schemas (output) | `<Model>Response` | `UserResponse`, `PostResponse` |
| SQLAlchemy models | singular `PascalCase` | `User`, `Post`, `Comment` |
| DB table names | `snake_case`, plural | `users`, `blog_posts` |
| Constants | `SCREAMING_SNAKE_CASE` | `ACCESS_TOKEN_EXPIRE_MINUTES` |
| Dependencies | `get_<thing>` | `get_db`, `get_current_user` |

## Route Handler Signatures
- Declare path/query/body parameters using **type annotations** — FastAPI derives them automatically.
- Use `Annotated[T, Depends(...)]` (the newer style) over `param: T = Depends(...)` for cleaner signatures.
- Keep route handlers thin — they should validate input, call a service function, and return the result. No business logic in handlers.

```python
from typing import Annotated

CurrentUser = Annotated[User, Depends(get_current_user)]
DBSession = Annotated[AsyncSession, Depends(get_db)]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: DBSession, _: CurrentUser) -> User:
    user = await user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

## SQLAlchemy Models
- Define all models with a `DeclarativeBase` subclass. Use `Mapped[T]` and `mapped_column()` (SQLAlchemy 2.x syntax) — not the legacy `Column()` API.
- Always define `__tablename__`.
- Use `created_at` / `updated_at` on every model with `server_default=func.now()` and `onupdate=func.now()`.

```python
from sqlalchemy import String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
```

## Settings
- Use `pydantic-settings` (`BaseSettings`) for all configuration. Never read `os.environ` directly in application code.
- Define a single `Settings` instance and import it where needed — don't instantiate `Settings()` in multiple places.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30

settings = Settings()
```
