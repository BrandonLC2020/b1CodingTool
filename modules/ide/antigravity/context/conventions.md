# Antigravity: Conventions

## Naming & Structure
- **Missions:** Use clear, action-oriented names for missions (e.g., `Add OAuth Login`, `Fix Memory Leak`).
- **Agents:** If multiple agents are deployed, name them based on their roles (e.g., `FrontendArchitect`, `TestRunner`, `DocsCrawler`).

## Execution Policies
- **Terminal:** Default to "Auto" for most commands. Require explicit confirmation for destructive actions like `rm -rf`, `git push --force`, or database migrations.
- **Browser:** Allow the agent to use the browser for searching documentation and verifying UI, but monitor for data exfiltration.

## Interaction Patterns
- **Plan First:** Always request a plan (`/plan`) before starting execution on any non-trivial task.
- **Verify Always:** Use `/verify` to prompt the agent to run tests and provide a walkthrough after completing a task.
- **Clear Constraints:** Provide explicit constraints (e.g., "Use Vanilla CSS", "Follow PEP 8") in the initial objective.
