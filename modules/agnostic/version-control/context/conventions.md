# Version Control: Conventions

## Commit Casing
Follow Conventional Commits:
| Type | Use Case |
|------|----------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation updates |
| `style` | Formatting, missing semi-colons, etc. |
| `refactor` | Code restructuring without behavior change |
| `test` | Adding or updating tests |
| `chore` | Build tasks, package updates |

## Commit Message Format
`<type>(<scope>): <description>`
Example: `feat(auth): add OAuth2 login flow`

## Ignoring Files
Required entries in every `.gitignore`:
```
# Secrets
.env
*.pem
*.key

# Local config
.agent/config.yaml (if local-only)
*.code-workspace

# OS files
.DS_Store
Thumbs.db
```
