# Python: Dependency Management with uv

## Overview
**uv** is the recommended package manager for all Python projects. it is extremely fast and manages both Python versions and dependencies using `pyproject.toml` and `uv.lock`.

## Common Commands
```bash
uv init                    # Initialize a new project
uv add <package>           # Add a production dependency
uv add --dev <package>     # Add a development dependency
uv sync                    # Sync environment with lockfile
uv run <command>           # Run a command in the project venv
uv python install 3.12     # Install a specific Python version
```

## pyproject.toml
Always use the standard PEP 621 `[project]` table in `pyproject.toml`.
