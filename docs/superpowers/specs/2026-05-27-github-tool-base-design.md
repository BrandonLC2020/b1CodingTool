# GitHub Tool Base — Module Library Expansion Design

**ClickUp:** [86b9zfzxv](https://app.clickup.com/t/86b9zfzxv) — *Create module: github workflows/actions/agents tool base*

**Goal:** Expand the module library to cover the full surface area of GitHub-based automation — self-hosted runners, AI coding agents acting on GitHub, and bot/automation accounts — by introducing three new sibling modules alongside the existing `github-actions/` module. Each new module reaches the maturity of the `aws/` module: manifest with skills + slash commands, three context files, an interactive scaffolding script, and at least two ready-to-use templates.

## Background

The existing `modules/deployment/github-actions/` module is intentionally lean: two context files (`best-practices.md`, `conventions.md`), one workflow template (`ci-pipeline.yml`), and no slash commands. It covers *workflows* well but says nothing about runners, AI agents, or bots. Meanwhile `modules/deployment/aws/` has matured into the reference shape for a "tool base" module: slash commands wired through `commands:`, interactive `*-init.sh` scripts under `scripts/`, and a `templates/` directory of `*.tmpl` files that the scripts render into a consumer project.

This spec extends the GitHub coverage by adding three new modules — `github-runners`, `github-ai-agents`, `github-bots` — modeled on the `aws/` shape. The existing `github-actions/` module is left unchanged.

## Architecture

Approach: **three new sibling modules** under `modules/deployment/`, each independently installable via `b1 install <path>` and each contributing its own context to the compiled `CLAUDE.md` / `GEMINI.md` / `AGENTS.md` via `b1 pair`.

### Filesystem layout

```
modules/deployment/
├── github-actions/                       (UNCHANGED — pre-existing)
├── github-runners/                       (NEW)
│   ├── b1-module.yaml
│   ├── context/
│   │   ├── best-practices.md
│   │   ├── conventions.md
│   │   └── agent-capabilities.md
│   ├── scripts/
│   │   ├── post-install.sh
│   │   └── runner-init.sh
│   └── templates/
│       ├── runner-systemd.service.tmpl
│       ├── runner-docker-compose.yml.tmpl
│       └── ephemeral-runner-workflow.yml.tmpl
├── github-ai-agents/                     (NEW)
│   ├── b1-module.yaml
│   ├── context/
│   │   ├── best-practices.md
│   │   ├── conventions.md
│   │   └── agent-capabilities.md
│   ├── scripts/
│   │   ├── post-install.sh
│   │   └── agents-init.sh
│   └── templates/
│       ├── claude-code-action.yml.tmpl
│       ├── codex-action.yml.tmpl
│       ├── agent-pr-review.yml.tmpl
│       └── AGENT_PERMISSIONS.md.tmpl
└── github-bots/                          (NEW)
    ├── b1-module.yaml
    ├── context/
    │   ├── best-practices.md
    │   ├── conventions.md
    │   └── agent-capabilities.md
    ├── scripts/
    │   ├── post-install.sh
    │   └── bots-init.sh
    └── templates/
        ├── dependabot.yml.tmpl
        ├── release-please.yml.tmpl
        └── triage-labeler.yml.tmpl
```

### Module manifests

Each `b1-module.yaml` uses `type: deployment` (the only `ModuleType` enum value that fits per `src/b1/core/schema.py`). Each declares its `skills:`, `commands:`, and a `post-install` hook.

**`github-runners/b1-module.yaml`**
```yaml
name: github-runners
version: 1.0.0
type: deployment
description: "Self-hosted GitHub Actions runner setup, security hardening, ephemeral patterns, and autoscaling guidance."
skills:
  - name: "Runner Setup Advisor"
    description: "Generates systemd, Docker, or Kubernetes manifests for self-hosted runners."
  - name: "Runner Security Auditor"
    description: "Audits runner deployments for isolation, ephemeral lifecycle, and least-privilege token usage."
  - name: "Autoscaling Configurator"
    description: "Recommends scaling strategies (ARC, philips-labs/terraform-aws-github-runner, etc.)."
commands:
  - name: "/gh-runners init"
    description: "Scaffold a self-hosted runner deployment (systemd / docker-compose / ephemeral workflow)."
  - name: "/gh-runners audit"
    description: "Audit existing runner configuration for security and isolation issues."
  - name: "/gh-runners scale-advice"
    description: "Recommend an autoscaling approach based on the project's workflow profile."
hooks:
  post-install: "scripts/post-install.sh"
```

**`github-ai-agents/b1-module.yaml`**
```yaml
name: github-ai-agents
version: 1.0.0
type: deployment
description: "Standards and scaffolding for AI coding agents (Claude Code, Codex, Copilot) acting through GitHub Actions and PRs."
skills:
  - name: "Agent Workflow Generator"
    description: "Generates workflow files that run AI agents (Claude Code Action, Codex, etc.) on issues, PRs, or @mentions."
  - name: "Agent Permission Auditor"
    description: "Audits workflows that grant tokens to AI agents for least-privilege and secret hygiene."
  - name: "Prompt File Manager"
    description: "Manages reusable prompt files under .github/agents/ and references them from workflows."
commands:
  - name: "/gh-agents init"
    description: "Interactively scaffold one or more AI agent workflows into .github/workflows/."
  - name: "/gh-agents add-claude"
    description: "Add a Claude Code Action workflow with a sensible default permissions block."
  - name: "/gh-agents audit-permissions"
    description: "Audit agent workflows for over-broad permissions or unsafe secret exposure."
hooks:
  post-install: "scripts/post-install.sh"
```

**`github-bots/b1-module.yaml`**
```yaml
name: github-bots
version: 1.0.0
type: deployment
description: "Standards and scaffolding for GitHub App / bot account automation: Dependabot, release-please, triage labelers."
skills:
  - name: "Bot Setup Advisor"
    description: "Recommends GitHub App vs PAT, least-privilege scopes, and audit-log expectations."
  - name: "Dependabot Configurator"
    description: "Generates a dependabot.yml tuned to the project's package ecosystems and cadence."
  - name: "Triage Bot Generator"
    description: "Generates labeler and triage workflows from a declared label taxonomy."
commands:
  - name: "/gh-bots init"
    description: "Interactively scaffold bot automation (dependabot, release-please, triage)."
  - name: "/gh-bots dependabot"
    description: "Generate a dependabot.yml after detecting the project's package managers."
  - name: "/gh-bots triage"
    description: "Generate a triage/labeler workflow from a label taxonomy."
hooks:
  post-install: "scripts/post-install.sh"
```

### Context files

Each module ships three markdown files compiled into the agent context by `ContextCompiler` (`src/b1/core/compiler.py`):

| File | Purpose |
|---|---|
| `best-practices.md` | Security & operational guidance: permissions blocks, secret hygiene, action pinning, isolation. Distinct from `github-actions/best-practices.md` — focused on the module's specific surface (runners, agents, bots). |
| `conventions.md` | File layout & naming: where to put runner config, agent prompt files, bot configs; label taxonomy; runner labels/groups. |
| `agent-capabilities.md` | Documents the slash commands and skills the module registers, mirroring `aws/context/agent-capabilities.md`. |

### Scaffolding scripts

Each module ships a `post-install.sh` (identical pattern to `aws/scripts/post-install.sh`: creates the per-module working directory in the consumer project if missing) and an interactive `*-init.sh` script that backs its primary `/gh-* init` slash command.

The interactive scripts follow the pattern set by `aws/scripts/proxy-init.sh`:

1. Prompt the user for the relevant choice (deployment target / agent vendor / bot type).
2. Resolve the matching `*.tmpl` file from the module's `templates/` directory.
3. Render with `envsubst`-style variable substitution.
4. Write to the appropriate consumer-project path (e.g. `.github/workflows/`, `infrastructure/runners/`).
5. Refuse to overwrite existing files unless `--force` is passed.

**Per-module working directories created by `post-install.sh`:**
- `github-runners` → `infrastructure/runners/`
- `github-ai-agents` → `.github/agents/` (for reusable prompt files)
- `github-bots` → `.github/` (root of `.github` — that's where `dependabot.yml` lives)

### Templates (high-level intent — actual contents drafted during implementation)

**`github-runners/templates/`**
- `runner-systemd.service.tmpl` — systemd unit for a long-lived self-hosted runner with `User=`, `WorkingDirectory=`, ephemeral env, restart policy.
- `runner-docker-compose.yml.tmpl` — containerized runner using a pinned `myoung34/github-runner`-style image with `EPHEMERAL=true` and a registration-token env.
- `ephemeral-runner-workflow.yml.tmpl` — a workflow demonstrating ARC or just-in-time runner labels (`runs-on: [self-hosted, ephemeral, ${{ matrix.label }}]`).

**`github-ai-agents/templates/`**
- `claude-code-action.yml.tmpl` — a workflow invoking the Claude Code Action on issue comments / PR `@claude` mentions, with `permissions:` scoped to `contents: read`, `pull-requests: write`, `issues: write`, no `id-token`.
- `codex-action.yml.tmpl` — equivalent for OpenAI Codex / equivalent agent.
- `agent-pr-review.yml.tmpl` — a workflow that auto-runs an agent reviewer on PRs, gated by label.
- `AGENT_PERMISSIONS.md.tmpl` — a repo-level policy doc explaining which permissions the agent workflows have and why; copied into the repo as `docs/AGENT_PERMISSIONS.md`.

**`github-bots/templates/`**
- `dependabot.yml.tmpl` — `version: 2` config with ecosystems pre-filled by the init script after probing the project.
- `release-please.yml.tmpl` — `googleapis/release-please-action` workflow with conventional-commits config.
- `triage-labeler.yml.tmpl` — `actions/labeler` workflow plus a starter `.github/labeler.yml`.

## Data flow

### Install
1. User runs `b1 install ./modules/deployment/github-ai-agents` (or via git URL).
2. The installer copies the module into `.agent/modules/github-ai-agents/` in the consumer project.
3. The `post-install` hook (`scripts/post-install.sh`) runs from the project root and creates `.github/agents/` if missing.
4. `b1 pair` regenerates `CLAUDE.md` / `GEMINI.md` / `AGENTS.md` to include the new module's context.

### Scaffold (e.g. `/gh-agents init`)
1. User invokes the slash command through their agent (Claude / Gemini / Codex).
2. The agent executes `.agent/modules/github-ai-agents/scripts/agents-init.sh`.
3. Script prompts: *which agent vendor?* (Claude Code / Codex / multiple) and *what trigger?* (`@mention` / PR-open / scheduled).
4. Script copies the matching `*.tmpl` from `templates/`, renders variables, and writes to `.github/workflows/`.
5. If a target file already exists, the script aborts unless `--force` is set.

## Error handling

- Manifests with unknown fields (typo, copy-paste error) fail validation at `ModuleConfig.from_yaml` time with the existing helpful suggestions list — no new error paths needed.
- Init scripts: `set -euo pipefail`; explicit checks for `command -v envsubst`, target-file existence (prompt or `--force`), and a writable `.github/` directory.
- Missing templates: scripts exit non-zero with a message naming the expected `templates/` path; this catches partial-install or corrupted-cache cases.

## Testing strategy

- **Unit (`tests/unit/`):** Extend `test_compiler.py` (or add `test_github_modules.py`) to load each new `b1-module.yaml` via `ModuleConfig.from_yaml` and assert the expected `skills` and `commands` are parsed. Pure Pydantic — fast, no I/O.
- **Integration (`tests/integration/`):** For each new module, install it into a tempdir, run `b1 pair`, and assert the resulting `CLAUDE.md` contains a fragment from `best-practices.md`.
- **Slow (`tests/slow/`, marker required):** Optional — actually run one `*-init.sh` script in a tempdir with stubbed stdin and assert the rendered template lands at the expected path. Not required for this ticket but listed for the plan to consider.
- **No changes to existing `github-actions/` tests.**

## Out of scope (deferred)

- Modifying or deprecating the existing `github-actions/` module.
- Cross-module shared context (the `_github-common/` idea from brainstorming) — would require a module-include primitive that doesn't exist in the compiler today.
- LLC overlays (`llc-github-*`) in `b1CodingTool-LLC-lib/` — separate ticket; mention but do not scaffold here.
- Implementation of the slash-command runtime itself (commands are *declared* in manifests but their execution path is the existing agent-driven script-runner; no new CLI plumbing required).

## Acceptance criteria

- [ ] Three new module directories exist under `modules/deployment/` with the file layout above.
- [ ] Each `b1-module.yaml` parses via `ModuleConfig.from_yaml` without error.
- [ ] Each module has three context files (`best-practices.md`, `conventions.md`, `agent-capabilities.md`) with non-placeholder content.
- [ ] Each module has at least one working `*-init.sh` script and at least two templates.
- [ ] `uv run pytest` passes (existing tests stay green; new unit tests added).
- [ ] `b1 install ./modules/deployment/github-ai-agents && b1 pair` produces a `CLAUDE.md` that references the new module.
- [ ] This spec is committed and an implementation plan exists at `docs/superpowers/plans/2026-05-27-github-tool-base-plan.md`.
