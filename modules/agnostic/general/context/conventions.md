# General: Conventions

## Git & Version Control
- **Commit Messages:** Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
  - `feat`: A new feature
  - `fix`: A bug fix
  - `docs`: Documentation only changes
  - `style`: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
  - `refactor`: A code change that neither fixes a bug nor adds a feature
  - `perf`: A code change that improves performance
  - `test`: Adding missing tests or correcting existing tests
  - `chore`: Changes to the build process or auxiliary tools and libraries
- **Branching:** Use descriptive branch names (e.g., `feat/add-login`, `fix/issue-123`).

## Documentation
- **README.md:** Every project must have a `README.md` explaining the project's purpose, setup, and usage.
- **GEMINI.md / CLAUDE.md:** Project-specific instructions for AI agents should be managed via `b1CodingTool` and committed to the repository.
- **Inline Comments:** Use comments to explain *why* something is done, not *what* is being done (the code should be self-explanatory).

## Naming & Style
- **Agnostic Naming:** Use clear, descriptive names for all entities (variables, functions, classes).
- **Consistency:** Adhere to the established patterns of the project, even if they differ from your personal preference.
