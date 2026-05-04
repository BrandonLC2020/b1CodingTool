# Python Dependency Management: uv vs Poetry

## Overview

Two tools dominate modern Python dependency management for FastAPI projects: **uv** and **Poetry**. Both manage virtual environments, dependencies, and lockfiles, but they differ significantly in philosophy, performance, and ecosystem alignment.

## uv

**uv** is a Rust-based Python package manager from Astral (makers of Ruff). It is a drop-in replacement for `pip`, `pip-tools`, `virtualenv`, and optionally `pyenv`.

### What uv Does Well
- **Speed.** Package resolution and installation are 10–100× faster than pip or Poetry. Large dependency trees (FastAPI + SQLAlchemy + Alembic + Pydantic) resolve in under a second.
- **Standard compliance.** Uses `pyproject.toml` with the PEP 621 `[project]` table — no vendor-specific format. The resulting `pyproject.toml` is readable by any standards-compliant tool.
- **Python version management.** `uv python install 3.12` replaces pyenv — one tool for both the interpreter and packages.
- **Lockfile.** `uv.lock` pins exact versions for reproducible installs across environments.
- **Serverless-friendly.** `uv sync --no-dev` installs only production dependencies — ideal for slim Docker images and Lambda layers.

### Common uv Commands
```bash
uv python install 3.12            # Install Python version
uv init                           # Create new project with pyproject.toml
uv add fastapi "uvicorn[standard]"  # Add dependencies
uv add --dev pytest pytest-asyncio httpx  # Add dev dependencies
uv sync                           # Install all deps from lockfile
uv sync --no-dev                  # Install prod deps only (Docker/CI)
uv run uvicorn app.main:app --reload   # Run dev server
uv run pytest                     # Run tests
uv lock                           # Update lockfile without installing
```

### pyproject.toml with uv
```toml
[project]
name = "my-fastapi-app"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.111",
    "uvicorn[standard]>=0.29",
    "sqlalchemy[asyncio]>=2.0",
    "alembic>=1.13",
    "asyncpg>=0.29",          # async Postgres driver
    "pydantic-settings>=2.0",
    "passlib[bcrypt]>=1.7",
    "python-jose[cryptography]>=3.3",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "httpx>=0.27",            # for AsyncClient in tests
    "ruff>=0.4",
    "mypy>=1.10",
]

[tool.uv]
# uv-specific settings (optional)
```

### When to Use uv
- New projects where you control the toolchain
- Serverless or containerized deployments where lean images and fast `pip install` matter
- Teams that want a single tool (Python version + packages)
- CI pipelines where install speed is a bottleneck
- This project (b1CodingTool) uses `uv` — use it here by default

---

## Poetry

**Poetry** is a Python packaging and dependency management tool that predates uv. It introduced the developer-friendly `pyproject.toml` workflow before PEP 621 was finalized, using its own `[tool.poetry]` section.

### What Poetry Does Well
- **Mature ecosystem.** Widely adopted — many existing FastAPI projects, tutorials, and CI examples use Poetry.
- **Publishing.** `poetry publish` builds and uploads packages to PyPI smoothly — useful if your FastAPI project is also a distributed library (e.g., a shared SDK).
- **Explicit dependency groups.** `[tool.poetry.group.dev.dependencies]` is a well-understood pattern across the community.
- **Plugin system.** Community plugins extend Poetry for dynamic versioning, dotenv injection, etc.

### Common Poetry Commands
```bash
poetry init                             # Create pyproject.toml interactively
poetry add fastapi "uvicorn[standard]"  # Add dependency
poetry add --group dev pytest httpx     # Add dev dependency
poetry install                          # Install from poetry.lock
poetry install --only main              # Prod deps only (Docker)
poetry run uvicorn app.main:app --reload
poetry run pytest
poetry update                           # Update all within constraints
poetry export -f requirements.txt --without-hashes > requirements.txt
```

### pyproject.toml with Poetry
```toml
[tool.poetry]
name = "my-fastapi-app"
version = "0.1.0"
description = ""

[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.111"
uvicorn = {extras = ["standard"], version = "^0.29"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0"}
alembic = "^1.13"
asyncpg = "^0.29"
pydantic-settings = "^2.0"
passlib = {extras = ["bcrypt"], version = "^1.7"}
python-jose = {extras = ["cryptography"], version = "^3.3"}

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
pytest-asyncio = "^0.23"
httpx = "^0.27"
ruff = "^0.4"
mypy = "^1.10"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### When to Use Poetry
- Existing projects already using Poetry — don't migrate without a clear reason
- Teams already familiar with Poetry
- When publishing your FastAPI app as a Python package to PyPI
- When a third-party deployment platform (some PaaS services) has built-in Poetry support

---

## Comparison Summary

| | uv | Poetry |
|---|---|---|
| **Install speed** | 10–100× faster | Baseline |
| **Python version mgmt** | Built-in (`uv python`) | Requires pyenv separately |
| **pyproject.toml format** | PEP 621 standard | `[tool.poetry]` (non-standard) |
| **Lockfile** | `uv.lock` | `poetry.lock` |
| **Docker layer caching** | Excellent (`uv sync --no-dev`) | Good (`poetry install --only main`) |
| **Package publishing** | `uv publish` (basic) | `poetry publish` (polished) |
| **Maturity** | Newer (stable since 2024) | Mature (since 2018) |
| **Ecosystem adoption** | Rapidly growing | Widely adopted |

## Docker Integration

Both tools work well in Docker. The key is to install only production dependencies in the final image.

**With uv (recommended):**
```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev   # install from lockfile, prod only
COPY . .
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**With Poetry:**
```dockerfile
FROM python:3.12-slim
RUN pip install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root
COPY . .
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Recommendation

**Use uv for new projects.** It is faster, follows open standards, handles Python version management, and produces lean Docker images. The ecosystem has converged on it as the modern default for FastAPI projects.

**Keep Poetry for existing projects** that already use it — migration has no functional benefit and introduces risk.

In either case, **commit the lockfile** (`uv.lock` or `poetry.lock`) to version control. Without it, installs across environments are not reproducible.
