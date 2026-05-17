# Docker Module Design Specification

## Background & Motivation
The user requires a deployment module for Docker within the `b1CodingTool`. The focus is on containerizing backend Python services (Django, FastAPI) for both local development (using Docker Compose) and production/CI (focusing on multi-stage builds, security, and efficiency). It intentionally excludes complex orchestrators like Kubernetes or Docker Swarm.

## Scope & Impact
- **In Scope:** Dockerfiles (multi-stage, non-root user), `docker-compose.yaml` (local dev with volumes, database/cache services), Python-specific containerization best practices, modular templates, and a `/docker init` skill.
- **Out of Scope:** Kubernetes, Docker Swarm, frontend containerization (unless trivial alongside backend).

## Proposed Solution (Service-First Approach)
The module will be built using a "Service-First" approach, providing modular building blocks rather than rigid stack templates.

### 1. Module Structure & Manifest
```yaml
name: docker
version: 1.0.0
type: deployment
description: "Guidelines, templates, and skills for Dockerizing backend services (local dev & production) without complex orchestrators."
commands:
  - name: "/docker init"
    description: "Initialize a Dockerfile and docker-compose.yml based on project requirements."
```
- `context/`: Guidelines.
- `templates/`: Modular snippets.
- `skills/`: Agent automation.

### 2. Core Guidelines (`context/`)
- **Local Dev:** Use `docker-compose.yaml`, volume mounts for code, live-reloading.
- **Production/CI:** Multi-stage builds, non-root execution, minimal base images.
- **Python Specifics:** Leverage `uv` (or `pip`/`poetry`) in builder stages, handle environment variables securely.

### 3. Templates (`templates/`)
- `dockerfile-python.tmpl`: A multi-stage Dockerfile optimized for Python (builder stage for dependencies, final stage running as a non-root user).
- `compose-postgres.tmpl`: A Compose service snippet for PostgreSQL, including a persistent volume and a basic health check.
- `compose-redis.tmpl`: A Compose service snippet for Redis.
- `compose-db-backup.tmpl`: A utility service snippet that runs a cron job (or simple script) to dump the PostgreSQL database to a mounted volume.

### 4. Skills (`skills/docker-init.md`)
- A skill that guides the agent when the user runs `/docker init`.
- It will prompt the agent to ask the user which services they need (e.g., "Do you need Postgres? Redis? DB Backup utility?").
- The agent will then assemble the requested template snippets into a cohesive `docker-compose.yml` and provide the `Dockerfile` tailored to the detected framework (Django or FastAPI).

## Alternatives Considered
- **Stack-Specific Templates:** Rejected in favor of the Service-First approach for better flexibility across different Python frameworks (Django, FastAPI).

## Verification
- Review the generated module structure (`modules/deployment/docker/`).
- Validate that the `b1-module.yaml` is correctly formatted.
- Ensure context files clearly articulate the local dev vs. production boundaries.
