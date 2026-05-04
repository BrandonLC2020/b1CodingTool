# Version Control: Best Practices

## Secret Protection (Critical)
- **Never Commit Secrets:** Do not commit API keys, passwords, private keys, or credentials to version control.
- **Use .env Files:** Store local secrets in `.env` files and ensure `.env` is listed in `.gitignore`.
- **Environment Variables:** Use system environment variables or secure vault services (e.g., GitHub Secrets, AWS Secrets Manager) for production credentials.
- **Git Hooks:** Use pre-commit hooks (e.g., `gitleaks`, `trufflehog`) to scan for secrets before they are committed.
- **History Cleanup:** If a secret is committed by mistake, use `git-filter-repo` or BFG Repo-Cleaner to purge it from the entire history. Revoke the secret immediately.

## Repository Hygiene
- **Atomic Commits:** Make small, focused commits that do one thing well. Avoid "giant" commits.
- **Descriptive Messages:** Follow the Conventional Commits specification (`feat:`, `fix:`, `chore:`, etc.).
- **Ignore files:** Maintain a robust `.gitignore` and agent-specific ignore files (`.geminiignore`, `.claudeignore`) to keep the repository clean.
- **Large Files:** Use Git LFS (Large File Storage) for binary assets or large data files.

## Branch Management
- **Main/Master Branch:** The `main` branch should always be deployable and protected.
- **Feature Branching:** Create short-lived feature branches (`feat/name`) for all new work.
- **Pull Requests:** Use PRs for code review and automated testing before merging into the main branch.
