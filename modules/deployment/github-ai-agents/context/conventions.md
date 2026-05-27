# GitHub AI Agents: Conventions

## File Layout
```
.github/
├── agents/                       # Reusable prompt files (markdown)
│   ├── code-reviewer.md
│   └── docs-writer.md
└── workflows/
    ├── claude-code.yml           # @claude mention handler
    ├── codex-action.yml          # Codex / equivalent
    └── agent-pr-review.yml       # Label-gated PR reviewer
docs/
└── AGENT_PERMISSIONS.md          # Repo policy: what each agent can do
```

## Naming
- **Workflow files:** `<agent-name>-<trigger>.yml` (e.g., `claude-code.yml`, `codex-pr-review.yml`).
- **Prompt files:** `<role>.md` (e.g., `code-reviewer.md`, `release-notes-writer.md`).
- **Labels:** `agent:<name>` (e.g., `agent:claude`) for routing; `bot:<name>` for filtering.

## Branching
- Agent-authored branches: `agent/<agent-name>/<short-slug>` (e.g., `agent/claude/fix-typo-in-readme`).
- Never merge agent commits directly to default branch — always via PR with at least one human approval.
