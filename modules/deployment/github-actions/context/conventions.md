# GitHub Actions: Conventions

## File Naming
- Workflows live in `.github/workflows/`.
- Use `kebab-case.yml` for filenames (e.g., `ci-pipeline.yml`, `auto-tag.yml`).

## Job Naming
- Use clear, descriptive names for jobs and steps (e.g., `Job: Run Unit Tests`, `Step: Install dependencies`).

## Directory Structure
```
.github/
├── workflows/
│   ├── main.yml        # Primary CI pipeline
│   └── release.yml     # Production deployment
├── actions/            # Custom local actions
└── scripts/            # Helper scripts for workflows
```
