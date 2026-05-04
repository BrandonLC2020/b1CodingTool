# GitHub Actions: Best Practices

## Workflow Design
- **Single Responsibility:** Each workflow file (`.github/workflows/*.yml`) should focus on a specific task (e.g., `test.yml`, `deploy.yml`).
- **Reuse Actions:** Use official or verified actions from the GitHub Marketplace. Prefer internal reusable workflows for organization-wide standards.
- **Fail Fast:** Place fast-running tasks (linting, unit tests) early in the pipeline to provide quick feedback.

## Security
- **Least Privilege:** Use the `permissions` key in workflow files to grant only the minimum necessary tokens (e.g., `contents: read`, `deployments: write`).
- **Secret Usage:** Use `${{ secrets.SECRET_NAME }}` for all credentials. Never echo secrets into logs.
- **Pin Actions:** Pin actions to a specific commit SHA rather than a version tag (e.g., `v1`) to prevent supply-chain attacks.
- **Environment Protection:** Use GitHub Environments with required reviewers for production deployments.

## Performance
- **Caching:** Use `actions/cache` to speed up dependency installation for npm, pip, etc.
- **Job Concurrency:** Use `concurrency` groups to cancel in-progress runs when a new commit is pushed to the same branch.
- **Matrix Builds:** Use `strategy/matrix` to test across multiple versions of languages or OSs efficiently.
