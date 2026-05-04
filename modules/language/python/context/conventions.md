# Python: Coding Conventions

## Style Guide
- **PEP 8:** Adhere strictly to PEP 8 standards. Use **Ruff** for linting and formatting.
- **Indentation:** Use 4 spaces per indentation level.
- **Line Length:** Limit lines to 88 or 100 characters (matching Black/Ruff defaults).

## Naming
| Entity | Convention | Example |
|--------|-----------|---------|
| Modules / Packages | `snake_case` | `my_package`, `utils.py` |
| Classes | `PascalCase` | `UserService`, `APIClient` |
| Functions / Methods | `snake_case` | `get_user_id()`, `save_record()` |
| Variables | `snake_case` | `user_count`, `is_active` |
| Constants | `SCREAMING_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |

## Imports
- Order imports using Ruff/isort:
  1. Standard library
  2. Third-party packages
  3. Local app/module imports
- Use absolute imports over relative imports where possible.
