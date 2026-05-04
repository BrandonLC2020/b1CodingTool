# Antigravity: Best Practices

## Agent Management (Mission Control)
- **Objective Definition:** Start every mission with a clear, high-level objective. Use "Planning Mode" to let the agent draft an implementation plan before writing code.
- **Task Granularity:** Break down large missions into manageable sub-tasks. Monitor the task list in the Mission Control panel to ensure the agent stays on track.
- **Human-in-the-Loop:** Use "Agent-Assisted" mode for production environments. Review the agent's plan and task list before authorizing the first execution.

## Verification & Artifacts
- **Implementation Plans:** Always review the agent's plan for architectural alignment and security considerations before implementation.
- **Browser Agent:** Use the built-in browser sub-agent for E2E testing and documentation lookup. It ensures that UI changes are verified in a real browser environment.
- **Walkthroughs:** Require the agent to provide a post-implementation walkthrough, including terminal logs and browser verification, to confirm the goal was met.

## Performance & Context
- **Selective Context:** Use `.geminiignore` or `.antigravityignore` to prevent the agent from processing irrelevant large directories like `node_modules` or `venv`.
- **Policy Enforcement:** Set terminal execution policies to "Auto" or "Turbo" only for safe, idempotent commands (e.g., `ls`, `git status`, `npm test`).
