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

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv export --no-dev --format requirements-txt > requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app
RUN groupadd -g 999 python && \
    useradd -r -u 999 -g python python
    
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .

RUN chown -R python:python /app
USER python

CMD ["python", "main.py"]
```

- [ ] **Step 2: Commit**
```bash
git add modules/deployment/docker/templates/dockerfile-python.tmpl
git commit -m "feat(docker): add multi-stage python dockerfile template"
```

---

### Task 3: The /docker init Skill

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

### Task 4: Integration Test for Rule Extraction

**Files:**
- Create: `tests/unit/test_rule_extractor_docker.py`

- [ ] **Step 1: Write test to verify Docker rules are extracted**
```python
import pytest
from b1.core.compiler import RuleExtractor
from pathlib import Path

def test_docker_rule_extraction(tmp_path):
    docker_context = tmp_path / "modules/deployment/docker/context"
    docker_context.mkdir(parents=True)
    (docker_context / "best-practices.md").write_text("# Docker: Best Practices\n- Use Compose")
    
    extractor = RuleExtractor(tmp_path)
    rules = extractor.extract_rules()
    
    assert any("Docker: Best Practices" in r.content for r in rules)
```

- [ ] **Step 2: Run test**
Run: `pytest tests/unit/test_rule_extractor_docker.py`

- [ ] **Step 3: Commit**
```bash
git add tests/unit/test_rule_extractor_docker.py
git commit -m "test(docker): add integration test for rule extraction"
```
