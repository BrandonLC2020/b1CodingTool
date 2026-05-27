# GitHub Bots: Agent Commands & Skills

## Recommended Skills
- **Bot Setup Advisor:** Recommends GitHub App vs PAT, least-privilege scopes, and audit-log expectations for a given automation goal.
- **Dependabot Configurator:** Detects the project's package managers (package.json, pyproject.toml, Dockerfile, etc.) and generates a tuned `dependabot.yml`.
- **Triage Bot Generator:** Generates a labeler workflow + `labeler.yml` from the project's existing label taxonomy.

## Common Agent Commands
- `/gh-bots init`: Interactively scaffold bot automation (dependabot, release-please, triage).
- `/gh-bots dependabot`: Generate a `dependabot.yml` after detecting the project's package managers.
- `/gh-bots triage`: Generate a triage/labeler workflow from a label taxonomy.

## Sync with b1
- `b1 install github-bots`: Adds bot context to the agent files.
- `b1 pair`: Re-compiles `CLAUDE.md` / `GEMINI.md` / `AGENTS.md` to include this module's context.
