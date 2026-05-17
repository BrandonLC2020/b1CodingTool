# Docker Deployment Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a modular Docker deployment module for `b1CodingTool` that supports local development (Compose) and production/CI hardening for Python services.

**Architecture:** A "Service-First" approach using modular template snippets and a `/docker init` skill to assemble them.

**Tech Stack:** Docker, Docker Compose, Python (Django, FastAPI), YAML, Markdown.

---

### Task 1: Module Scaffolding & Manifest

**Files:**
- Create: `modules/deployment/docker/b1-module.yaml`

- [ ] **Step 1: Create the directory structure**
Run: `mkdir -p modules/deployment/docker/{context,templates,skills,scripts}`

- [ ] **Step 2: Create the manifest file**
```yaml
name: docker
version: 1.0.0
type: deployment
description: "Guidelines, templates, and skills for Dockerizing backend services (local dev & production) without complex orchestrators."
commands:
  - name: "/docker init"
    description: "Initialize a Dockerfile and docker-compose.yml based on project requirements."
```

- [ ] **Step 3: Commit**
```bash
git add modules/deployment/docker/b1-module.yaml
git commit -m "feat(docker): initialize docker module and manifest"
```

---

### Task 2: Core Context Guidelines

**Files:**
- Create: `modules/deployment/docker/context/best-practices.md`
- Create: `modules/deployment/docker/context/python-conventions.md`

- [ ] **Step 1: Create best practices context**
```markdown
# Docker: Best Practices

## Local Development
- **Docker Compose:** Use `docker-compose.yaml` to orchestrate services locally.
- **Volumes:** Mount project directories as volumes for live-reloading.
- **Environment Variables:** Use `.env` files for local configuration.

## Production & CI
- **Multi-stage Builds:** Separate the build environment from the runtime environment to minimize image size.
- **Non-Root User:** Always run the application process as a non-privileged user.
- **Health Checks:** Include health checks in Compose files for reliable service dependencies.
- **No Orchestrators:** Focus on core container lifecycle; do not include Swarm or Kubernetes configs.
```

- [ ] **Step 2: Create Python-specific conventions**
```markdown
# Docker: Python Conventions

## Image Selection
- Use official Python "slim" images (e.g., `python:3.12-slim`) for a balance of size and compatibility.

## Dependency Management
- **UV:** Prefer `uv` for fast dependency installation.
- **Layer Caching:** Copy requirements files and install dependencies before copying the rest of the application code.

## Production Servers
- **Django:** Use `gunicorn` or `uvicorn` (with gunicorn worker).
- **FastAPI:** Use `uvicorn`.
```

- [ ] **Step 3: Commit**
```bash
git add modules/deployment/docker/context/
git commit -m "docs(docker): add best practices and python conventions context"
```

---

### Task 3: Modular Templates (Compose)

**Files:**
- Create: `modules/deployment/docker/templates/compose-postgres.tmpl`
- Create: `modules/deployment/docker/templates/compose-redis.tmpl`
- Create: `modules/deployment/docker/templates/compose-db-backup.tmpl`

- [ ] **Step 1: Create Postgres template**
```yaml
  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=${DB_NAME:-app}
      - POSTGRES_USER=${DB_USER:-postgres}
      - POSTGRES_PASSWORD=${DB_PASSWORD:-postgres}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres} -d ${DB_NAME:-app}"]
      interval: 10s
      timeout: 5s
      retries: 5
```

- [ ] **Step 2: Create Redis template**
```yaml
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5
```

- [ ] **Step 3: Create DB Backup template**
```yaml
  db-backup:
    image: prodrigestivill/postgres-backup-local:16-alpine
    restart: always
    volumes:
      - ./backups:/backups
    depends_on:
      db:
        condition: service_healthy
    environment:
      - POSTGRES_HOST=db
      - POSTGRES_DB=${DB_NAME:-app}
      - POSTGRES_USER=${DB_USER:-postgres}
      - POSTGRES_PASSWORD=${DB_PASSWORD:-postgres}
      - SCHEDULE=@daily
      - BACKUP_KEEP_DAYS=7
```

- [ ] **Step 4: Commit**
```bash
git add modules/deployment/docker/templates/
git commit -m "feat(docker): add modular compose templates"
```

---

### Task 4: Modular Templates (Dockerfile)

**Files:**
- Create: `modules/deployment/docker/templates/dockerfile-python.tmpl`

- [ ] **Step 1: Create multi-stage Python Dockerfile template**
```dockerfile
# Stage 1: Builder
FROM python:3.12-slim AS builder

# Install uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables for uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

# Install dependencies first for better caching
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# Stage 2: Runtime
FROM python:3.12-slim

# Create a non-privileged user
RUN groupadd -g 999 python && \
    useradd -r -u 999 -g python python

WORKDIR /app

# Copy the virtual environment from the builder
COPY --from=builder --chown=python:python /app/.venv /app/.venv

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code with correct ownership
COPY --chown=python:python . .

USER python

# Default command (can be overridden)
CMD ["python", "main.py"]
```

- [ ] **Step 2: Commit**
```bash
git add modules/deployment/docker/templates/dockerfile-python.tmpl
git commit -m "feat(docker): add multi-stage python dockerfile template"
```

---

### Task 5: The /docker init Skill

**Files:**
- Create: `modules/deployment/docker/skills/docker-init.md`

- [ ] **Step 1: Create the skill instructions**
```markdown
# Skill: /docker init

When the user runs `/docker init`, follow this procedure:

1. **Analyze Project:** Identify if the project is Django, FastAPI, or another Python framework.
2. **Consult User:** Ask which of the following services are needed:
   - PostgreSQL
   - Redis
   - DB Backup Utility
3. **Assemble Files:**
   - Generate a `Dockerfile` using the `dockerfile-python.tmpl` as a base, adjusting the `CMD` and dependency steps as needed.
   - Generate a `docker-compose.yml` that includes the app service and the requested modular templates from the `templates/` directory.
4. **Environment:** Remind the user to set up a `.env` file with the required variables.
```

- [ ] **Step 2: Commit**
```bash
git add modules/deployment/docker/skills/docker-init.md
git commit -m "feat(docker): add /docker init skill"
```

---

### Task 6: Integration Test for Context Compilation

**Files:**
- Create: `tests/unit/test_docker_context.py`

- [ ] **Step 1: Write test to verify Docker context is compiled**
```python
import pytest
from b1.core.compiler import ContextCompiler
from pathlib import Path

def test_docker_context_compilation(tmp_path):
    # Setup a mock project structure
    modules_dir = tmp_path / ".agent" / "modules" / "docker" / "context"
    modules_dir.mkdir(parents=True)
    (modules_dir / "best-practices.md").write_text("# Docker: Best Practices\n- Use Compose", encoding="utf-8")
    
    # Compile context
    compiler = ContextCompiler(tmp_path)
    result = compiler.compile()
    
    # Verify the context was included
    assert "Docker: Best Practices" in result
    assert "<!-- b1CodingTool: Module Context [docker] - best-practices.md -->" in result
```

- [ ] **Step 2: Run test**
Run: `pytest tests/unit/test_docker_context.py`

- [ ] **Step 3: Commit**
```bash
git add tests/unit/test_docker_context.py
git commit -m "test(docker): add integration test for context compilation"
```

