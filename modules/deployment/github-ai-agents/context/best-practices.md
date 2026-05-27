# GitHub AI Agents: Best Practices

## Permissions
- **Default to read-only.** Start agent workflows with `permissions: contents: read` and add scopes only as needed. Never use `permissions: write-all`.
- **No `id-token: write` unless OIDC is required.** This scope can be used to mint cloud credentials.
- **Restrict secrets at the environment level.** Sensitive secrets (deploy keys, API keys with billing impact) belong in protected GitHub Environments with required reviewers, not in repo-level secrets accessible to PR workflows.

## Triggering
- **Gate agent runs on a label or a maintainer comment.** Do not trigger agents from `pull_request` on forks — use `pull_request_target` with explicit checkout of the merge ref and tight permissions, or require an `agent:run` label set by a maintainer.
- **Add a cost guard.** Agent runs cost money (API tokens + compute). Use `concurrency` to cancel stale runs and `timeout-minutes` to bound worst case.

## Prompt Hygiene
- **Keep prompts in version control** under `.github/agents/` so they are auditable and reviewable.
- **Never paste user-controlled input directly into the system prompt.** Treat issue/PR bodies as untrusted and sandbox them in user-role content.
- **Use deterministic models for review-style tasks** and reserve agentic models for genuine code-writing.

## Auditability
- Agent commits should be authored by a clearly-identified GitHub App or bot account, never by a human maintainer.
- Tag agent PRs with a `bot:agent-name` label so they are filterable in search and analytics.
