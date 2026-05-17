# Docker: Python Conventions

## Image Selection
- Use official Python "slim" images (e.g., `python:3.12-slim`) for a balance of size and compatibility.

## Dependency Management
- **UV:** Prefer `uv` for fast dependency installation.
- **Layer Caching:** Copy requirements files and install dependencies before copying the rest of the application code.

## Production Servers
- **Django:** Use `gunicorn` or `uvicorn` (with gunicorn worker).
- **FastAPI:** Use `uvicorn`.
