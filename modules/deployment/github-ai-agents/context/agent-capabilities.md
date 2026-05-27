# GitHub AI Agents: Agent Commands & Skills

## Recommended Skills
- **Agent Workflow Generator:** Generates a GitHub Actions workflow that runs a chosen AI agent (Claude Code Action, Codex, etc.) on a chosen trigger (`@mention`, label, scheduled, PR-opened).
- **Agent Permission Auditor:** Scans `.github/workflows/` for agent workflows and flags over-broad `permissions:` blocks or risky secret exposure.
- **Prompt File Manager:** Creates and updates reusable prompt files in `.github/agents/` and ensures workflows reference them via `prompt_file:` inputs.

## Common Agent Commands
- `/gh-agents init`: Interactively scaffold one or more AI agent workflows into `.github/workflows/`.
- `/gh-agents add-claude`: Add a Claude Code Action workflow with a sensible default permissions block.
- `/gh-agents audit-permissions`: Audit existing agent workflows for over-broad permissions or unsafe secret exposure.

## Sync with b1
- `b1 install github-ai-agents`: Creates `.github/agents/` and adds AI-agent context to the agent files.
- `b1 pair`: Re-compiles `CLAUDE.md` / `GEMINI.md` / `AGENTS.md` to include this module's context.
