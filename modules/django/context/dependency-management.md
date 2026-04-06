# Python Dependency Management: uv vs Poetry

## Overview

Two tools dominate modern Python dependency management for Django projects: **uv** and **Poetry**. Both manage virtual environments, dependencies, and lockfiles, but they differ significantly in philosophy, performance, and ecosystem alignment.

## uv

**uv** is a Rust-based Python package manager from Astral (makers of Ruff). It is a drop-in replacement for `pip`, `pip-tools`, `virtualenv`, and optionally `pyenv`.

### What uv Does Well
- **Speed.** Package resolution and installation are 10–100× faster than pip or Poetry. Large dependency trees (Django + DRF + Celery + Sentry) resolve in under a second.
- **Standard compliance.** Uses `pyproject.toml` with the PEP 621 `[project]` table — no vendor-specific format. The resulting `pyproject.toml` is readable by any standards-compliant tool.
- **Python version management.** `uv python install 3.12` replaces pyenv — one tool for both the interpreter and packages.
- **Lockfile.** `uv.lock` pins exact versions for reproducible installs across environments.
- **Workspace support.** Manages monorepos with multiple Python packages natively.

### Common uv Commands
```bash
uv python install 3.12        # Install Python version
uv init                       # Create new project with pyproject.toml
uv add django djangorestframework  # Add dependencies
uv add --dev pytest pytest-django  # Add dev dependencies
uv sync                       # Install all deps from lockfile
uv sync --no-dev              # Install prod deps only (CI/containers)
uv run python manage.py runserver  # Run command in project venv
uv run pytest                 # Run tests
uv lock                       # Update lockfile without installing
uv pip install <pkg>          # One-off install (pip compatibility mode)
```

### pyproject.toml with uv
```toml
[project]
name = "my-django-app"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "django>=5.0",
    "djangorestframework>=3.15",
    "psycopg[async]>=3.1",
    "pydantic-settings>=2.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-django>=4.8",
    "factory-boy>=3.3",
    "ruff>=0.4",
]

[tool.uv]
dev-dependencies = []   # legacy field — prefer dependency-groups above
```

### When to Use uv
- New projects where you control the toolchain
- Teams that want a single tool (Python version + packages)
- CI pipelines where install speed matters
- Projects already using Ruff (same ecosystem, same philosophy)
- This project (b1CodingTool) uses `uv` — use it here by default

---

## Poetry

**Poetry** is a Python packaging and dependency management tool that predates uv. It introduced the developer-friendly `pyproject.toml` workflow before PEP 621 was finalized, using its own `[tool.poetry]` section.

### What Poetry Does Well
- **Mature ecosystem.** Widely adopted — many existing Django projects, tutorials, and CI examples use Poetry.
- **Publishing.** `poetry publish` builds and uploads packages to PyPI with minimal config — slightly smoother than `uv publish` for library authors.
- **Explicit dependency groups.** `[tool.poetry.group.dev.dependencies]` has been the standard pattern for years; most Django devs recognize it immediately.
- **Plugin system.** Community plugins extend Poetry for dynamic versioning, dotenv loading, etc.

### Common Poetry Commands
```bash
poetry init                   # Create new pyproject.toml interactively
poetry add django             # Add dependency
poetry add --group dev pytest # Add dev dependency
poetry install                # Install from poetry.lock
poetry install --only main    # Install prod deps only
poetry run python manage.py runserver
poetry run pytest
poetry update                 # Update all deps within constraints
poetry lock                   # Update lockfile without installing
poetry export -f requirements.txt --without-hashes > requirements.txt
```

### pyproject.toml with Poetry
```toml
[tool.poetry]
name = "my-django-app"
version = "0.1.0"
description = ""
packages = [{include = "app"}]

[tool.poetry.dependencies]
python = "^3.12"
django = "^5.0"
djangorestframework = "^3.15"
psycopg = {extras = ["async"], version = "^3.1"}

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
pytest-django = "^4.8"
factory-boy = "^3.3"
ruff = "^0.4"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### When to Use Poetry
- Existing projects already using Poetry — don't migrate unless there's a reason
- Teams familiar with Poetry where switching would cause friction
- Library/package authors who publish to PyPI frequently
- When a third-party service or tutorial assumes Poetry (some PaaS platforms have Poetry-specific build steps)

---

## Comparison Summary

| | uv | Poetry |
|---|---|---|
| **Install speed** | 10–100× faster | Baseline |
| **Python version mgmt** | Built-in (`uv python`) | Requires pyenv separately |
| **pyproject.toml format** | PEP 621 standard | `[tool.poetry]` (non-standard) |
| **Lockfile** | `uv.lock` | `poetry.lock` |
| **Package publishing** | `uv publish` (basic) | `poetry publish` (polished) |
| **Maturity** | Newer (stable since 2024) | Mature (since 2018) |
| **Ecosystem adoption** | Rapidly growing | Widely adopted |
| **Plugin system** | No | Yes |

## Recommendation

**Use uv for new projects.** It is faster, follows open standards, and handles Python version management in one tool. The ecosystem has converged on it as the modern default.

**Keep Poetry for existing projects** that already use it — migration has no functional benefit and introduces risk.

In either case, **commit the lockfile** (`uv.lock` or `poetry.lock`) to version control. Without it, installs across environments are not reproducible.
