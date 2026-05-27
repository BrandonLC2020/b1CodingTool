# GitHub Tool Base Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add three new sibling modules under `modules/deployment/` — `github-runners`, `github-ai-agents`, `github-bots` — each modeled on the `aws/` module's shape (manifest + 3 context files + post-install + interactive init script + templates).

**Architecture:** Each module is independently installable via `b1 install`. A unit test up front pins the manifest contracts (TDD red), then each module is built file-by-file until that test goes green. A final integration smoke test installs one module into a tempdir, runs `b1 pair`, and asserts the compiled `CLAUDE.md` references the module.

**Tech Stack:** Python 3.12 + Pydantic (manifest parsing), YAML (manifests, templates), Bash (post-install + init scripts), Markdown (context files), `pytest` (testing via `uv run pytest`).

**Spec:** `docs/superpowers/specs/2026-05-27-github-tool-base-design.md`

---

### Task 1: Add Failing Unit Test for All Three Manifests

**Files:**
- Create: `tests/unit/test_github_modules.py`

- [ ] **Step 1: Write the failing test file**

Create `tests/unit/test_github_modules.py` with the following content:

```python
"""Tests that the three new GitHub tool-base manifests parse correctly via ModuleConfig."""
from pathlib import Path

import pytest

from b1.core.schema import ModuleConfig, ModuleType

MODULES_ROOT = Path(__file__).resolve().parents[2] / "modules" / "deployment"


def _load(module_name: str) -> ModuleConfig:
    return ModuleConfig.from_yaml(MODULES_ROOT / module_name / "b1-module.yaml")


@pytest.mark.parametrize(
    "module_name,expected_command_prefix",
    [
        ("github-runners", "/gh-runners"),
        ("github-ai-agents", "/gh-agents"),
        ("github-bots", "/gh-bots"),
    ],
)
def test_github_module_manifest_parses(module_name, expected_command_prefix):
    config = _load(module_name)
    assert config.name == module_name
    assert config.type == ModuleType.deployment
    assert config.version == "1.0.0"
    assert len(config.skills) >= 2, f"{module_name} should declare at least 2 skills"
    assert len(config.commands) >= 3, f"{module_name} should declare at least 3 commands"
    assert all(
        c.name.startswith(expected_command_prefix) for c in config.commands
    ), f"all commands in {module_name} should start with {expected_command_prefix}"
    assert config.hooks.get("post-install") == "scripts/post-install.sh"


@pytest.mark.parametrize(
    "module_name,expected_files",
    [
        (
            "github-runners",
            [
                "context/best-practices.md",
                "context/conventions.md",
                "context/agent-capabilities.md",
                "scripts/post-install.sh",
                "scripts/runner-init.sh",
                "templates/runner-systemd.service.tmpl",
                "templates/runner-docker-compose.yml.tmpl",
                "templates/ephemeral-runner-workflow.yml.tmpl",
            ],
        ),
        (
            "github-ai-agents",
            [
                "context/best-practices.md",
                "context/conventions.md",
                "context/agent-capabilities.md",
                "scripts/post-install.sh",
                "scripts/agents-init.sh",
                "templates/claude-code-action.yml.tmpl",
                "templates/codex-action.yml.tmpl",
                "templates/agent-pr-review.yml.tmpl",
                "templates/AGENT_PERMISSIONS.md.tmpl",
            ],
        ),
        (
            "github-bots",
            [
                "context/best-practices.md",
                "context/conventions.md",
                "context/agent-capabilities.md",
                "scripts/post-install.sh",
                "scripts/bots-init.sh",
                "templates/dependabot.yml.tmpl",
                "templates/release-please.yml.tmpl",
                "templates/triage-labeler.yml.tmpl",
            ],
        ),
    ],
)
def test_github_module_artifacts_exist(module_name, expected_files):
    base = MODULES_ROOT / module_name
    missing = [f for f in expected_files if not (base / f).is_file()]
    assert not missing, f"{module_name} is missing: {missing}"


@pytest.mark.parametrize(
    "module_name,init_script",
    [
        ("github-runners", "scripts/runner-init.sh"),
        ("github-ai-agents", "scripts/agents-init.sh"),
        ("github-bots", "scripts/bots-init.sh"),
    ],
)
def test_init_scripts_are_executable(module_name, init_script):
    import os
    path = MODULES_ROOT / module_name / init_script
    assert path.is_file(), f"{path} missing"
    assert os.access(path, os.X_OK), f"{path} is not executable"
```

- [ ] **Step 2: Run the test and confirm it fails**

Run: `uv run pytest tests/unit/test_github_modules.py -v`
Expected: All 9 parametrized test cases FAIL (3 modules × 3 test functions). Errors should mention missing `b1-module.yaml` files or missing artifact files. This is the TDD red phase that the next three tasks turn green.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_github_modules.py
git commit -m "test: add failing manifest+artifact tests for github tool base modules"
```

---

### Task 2: Build `github-runners` Module

**Files:**
- Create: `modules/deployment/github-runners/b1-module.yaml`
- Create: `modules/deployment/github-runners/context/best-practices.md`
- Create: `modules/deployment/github-runners/context/conventions.md`
- Create: `modules/deployment/github-runners/context/agent-capabilities.md`
- Create: `modules/deployment/github-runners/scripts/post-install.sh`
- Create: `modules/deployment/github-runners/scripts/runner-init.sh`
- Create: `modules/deployment/github-runners/templates/runner-systemd.service.tmpl`
- Create: `modules/deployment/github-runners/templates/runner-docker-compose.yml.tmpl`
- Create: `modules/deployment/github-runners/templates/ephemeral-runner-workflow.yml.tmpl`

- [ ] **Step 1: Create the manifest**

Create `modules/deployment/github-runners/b1-module.yaml`:

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

- [ ] **Step 2: Create `context/best-practices.md`**

```markdown
# GitHub Self-Hosted Runners: Best Practices

## Isolation
- **Never run untrusted workflows on persistent runners.** A persistent runner that processes PR-triggered workflows from forks is a remote-code-execution channel into your infrastructure.
- **Prefer ephemeral runners** (`--ephemeral` flag, or just-in-time tokens) that exit after a single job. This forces a clean machine state per job and contains compromise.
- **Run each runner as a dedicated, low-privilege OS user.** Never as root. Never as a developer's account.
- **Separate runner pools by trust tier.** Use distinct labels (e.g., `trusted`, `untrusted`, `prod`) and pin sensitive workflows to the appropriate pool.

## Network & Secrets
- Runners only need outbound access to GitHub's API/registry and to whatever your build needs. Block everything else.
- Do not store long-lived `PAT`s on runners. Use GitHub App installation tokens or OIDC-issued cloud credentials.
- Mount build secrets at job time via the Actions `secrets` context — never bake them into the runner image.

## Lifecycle
- Image runners declaratively (Packer, container image, cloud-init). Treat the runner host as cattle, not pets.
- For autoscaling, prefer [Actions Runner Controller (ARC)](https://github.com/actions/actions-runner-controller) on Kubernetes or the `philips-labs/terraform-aws-github-runner` module on AWS.
- Set a hard maximum runtime (`timeout-minutes`) on every job that runs on self-hosted infrastructure.

## Updates
- Keep the runner agent updated. Auto-update is on by default; do not disable it without a replacement plan.
- Patch the runner host OS on a regular cadence; integrate into your normal image-bake pipeline.
```

- [ ] **Step 3: Create `context/conventions.md`**

```markdown
# GitHub Self-Hosted Runners: Conventions

## Labels
Use a three-axis label scheme:
- **Trust:** `trusted` / `untrusted`
- **OS:** `linux` / `macos` / `windows`
- **Capability:** `gpu`, `arm64`, `large`, etc.

Workflows target the combination they need: `runs-on: [self-hosted, linux, trusted, arm64]`.

## Runner Groups
- Use runner groups (org-level) to gate which repos can use which pools.
- Production-deploy pools should be restricted to a single deploy repo or a small allowlist.

## Directory Layout in Consumer Project
```
infrastructure/runners/
├── systemd/                # Long-lived runner unit files
├── docker/                 # Containerized runner compose files
└── arc/                    # Kubernetes ARC manifests
```

## Naming
- Runner hostnames: `<env>-<pool>-<index>` (e.g., `prod-linux-trusted-01`).
- Image tags: `runner-<os>-<date>` (e.g., `runner-ubuntu2204-20260527`).
```

- [ ] **Step 4: Create `context/agent-capabilities.md`**

```markdown
# GitHub Self-Hosted Runners: Agent Commands & Skills

## Recommended Skills
- **Runner Setup Advisor:** Generates systemd unit files, docker-compose configs, or ARC manifests for self-hosted runners.
- **Runner Security Auditor:** Audits an existing runner deployment for isolation, ephemeral lifecycle, and least-privilege token usage.
- **Autoscaling Configurator:** Recommends a scaling strategy (ARC on Kubernetes, philips-labs Terraform module on AWS, GitHub-hosted with self-hosted overflow).

## Common Agent Commands
- `/gh-runners init`: Interactively scaffold a self-hosted runner deployment (systemd, docker-compose, or ephemeral workflow).
- `/gh-runners audit`: Audit existing runner configuration files under `infrastructure/runners/` for security and isolation issues.
- `/gh-runners scale-advice`: Recommend an autoscaling approach based on the project's workflow concurrency profile.

## Sync with b1
- `b1 install github-runners`: Initializes `infrastructure/runners/` and adds runner context to the agent files.
- `b1 pair`: Re-compiles `CLAUDE.md` / `GEMINI.md` / `AGENTS.md` to include this module's context.
```

- [ ] **Step 5: Create `scripts/post-install.sh`**

```bash
#!/bin/bash
set -e

# This script is executed from the project root.
# Located at .agent/modules/github-runners/scripts/post-install.sh after install.

RUNNERS_DIR="infrastructure/runners"

echo "Initializing self-hosted runner infrastructure structure..."

if [ ! -d "$RUNNERS_DIR" ]; then
    mkdir -p "$RUNNERS_DIR/systemd"
    mkdir -p "$RUNNERS_DIR/docker"
    mkdir -p "$RUNNERS_DIR/arc"
    echo "Created $RUNNERS_DIR directory structure."
else
    echo "$RUNNERS_DIR already exists, skipping creation."
fi

echo "github-runners module setup complete."
```

- [ ] **Step 6: Create `scripts/runner-init.sh`**

```bash
#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")/templates"
TARGET_BASE="${PWD}/infrastructure/runners"

echo "=== Self-Hosted Runner Setup ==="
echo "Select deployment style:"
echo "  1) systemd unit (long-lived runner on a Linux host)"
echo "  2) docker-compose (containerized runner, ephemeral)"
echo "  3) ephemeral workflow example (just-in-time runners)"
read -p "Selection (1, 2, or 3): " CHOICE

force=false
if [[ "${1:-}" == "--force" ]]; then
    force=true
fi

copy_template() {
    local src="$1"
    local dst="$2"
    mkdir -p "$(dirname "$dst")"
    if [ -f "$dst" ] && [ "$force" != "true" ]; then
        read -p "$dst already exists. Overwrite? (y/N) " OW
        [[ ! "$OW" =~ ^[Yy]$ ]] && { echo "Skipping."; return; }
    fi
    if [ ! -f "$src" ]; then
        echo "ERROR: template not found at $src" >&2
        exit 1
    fi
    cp "$src" "$dst"
    echo "Created $dst"
}

case "$CHOICE" in
    1)
        copy_template "$TEMPLATE_DIR/runner-systemd.service.tmpl" "$TARGET_BASE/systemd/github-runner.service"
        echo "Edit the service file to set the runner's user, URL, and registration token, then:"
        echo "  sudo cp $TARGET_BASE/systemd/github-runner.service /etc/systemd/system/"
        echo "  sudo systemctl daemon-reload && sudo systemctl enable --now github-runner"
        ;;
    2)
        copy_template "$TEMPLATE_DIR/runner-docker-compose.yml.tmpl" "$TARGET_BASE/docker/docker-compose.yml"
        echo "Set RUNNER_TOKEN and REPO_URL in your environment, then: docker compose up -d"
        ;;
    3)
        copy_template "$TEMPLATE_DIR/ephemeral-runner-workflow.yml.tmpl" "${PWD}/.github/workflows/ephemeral-runner-example.yml"
        ;;
    *)
        echo "Invalid selection." >&2
        exit 1
        ;;
esac

echo "Done."
```

- [ ] **Step 7: Create `templates/runner-systemd.service.tmpl`**

```ini
[Unit]
Description=GitHub Actions Self-Hosted Runner
After=network.target

[Service]
Type=simple
User={{RUNNER_USER}}
WorkingDirectory=/home/{{RUNNER_USER}}/actions-runner
ExecStart=/home/{{RUNNER_USER}}/actions-runner/run.sh
Restart=on-failure
RestartSec=15
# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/home/{{RUNNER_USER}}/actions-runner
# Resource limits
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

- [ ] **Step 8: Create `templates/runner-docker-compose.yml.tmpl`**

```yaml
# Containerized self-hosted runner. Set RUNNER_TOKEN, REPO_URL, RUNNER_NAME in env.
# Uses myoung34/github-runner — pin to a specific tag in production.
services:
  runner:
    image: myoung34/github-runner:ubuntu-jammy
    container_name: ${RUNNER_NAME:-github-runner}
    restart: unless-stopped
    environment:
      RUNNER_NAME: ${RUNNER_NAME:-github-runner}
      RUNNER_TOKEN: ${RUNNER_TOKEN}
      REPO_URL: ${REPO_URL}
      LABELS: self-hosted,linux,docker,untrusted
      EPHEMERAL: "true"
      DISABLE_AUTO_UPDATE: "false"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    security_opt:
      - no-new-privileges:true
```

- [ ] **Step 9: Create `templates/ephemeral-runner-workflow.yml.tmpl`**

```yaml
# Example workflow targeting an ephemeral self-hosted runner pool.
# Assumes runners are registered with labels: self-hosted, linux, ephemeral.
name: example-ephemeral-job

on:
  workflow_dispatch:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: false

jobs:
  build:
    runs-on: [self-hosted, linux, ephemeral]
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: echo "Replace with your build steps."
```

- [ ] **Step 10: Make scripts executable and run the test for this module**

```bash
chmod +x modules/deployment/github-runners/scripts/post-install.sh
chmod +x modules/deployment/github-runners/scripts/runner-init.sh
uv run pytest tests/unit/test_github_modules.py -v -k github-runners
```

Expected: The three `github-runners` parametrized cases pass; `github-ai-agents` and `github-bots` still fail.

- [ ] **Step 11: Commit**

```bash
git add modules/deployment/github-runners/
git commit -m "feat(modules): add github-runners module for self-hosted runner setup"
```

---

### Task 3: Build `github-ai-agents` Module

**Files:**
- Create: `modules/deployment/github-ai-agents/b1-module.yaml`
- Create: `modules/deployment/github-ai-agents/context/best-practices.md`
- Create: `modules/deployment/github-ai-agents/context/conventions.md`
- Create: `modules/deployment/github-ai-agents/context/agent-capabilities.md`
- Create: `modules/deployment/github-ai-agents/scripts/post-install.sh`
- Create: `modules/deployment/github-ai-agents/scripts/agents-init.sh`
- Create: `modules/deployment/github-ai-agents/templates/claude-code-action.yml.tmpl`
- Create: `modules/deployment/github-ai-agents/templates/codex-action.yml.tmpl`
- Create: `modules/deployment/github-ai-agents/templates/agent-pr-review.yml.tmpl`
- Create: `modules/deployment/github-ai-agents/templates/AGENT_PERMISSIONS.md.tmpl`

- [ ] **Step 1: Create the manifest**

Create `modules/deployment/github-ai-agents/b1-module.yaml`:

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

- [ ] **Step 2: Create `context/best-practices.md`**

```markdown
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
```

- [ ] **Step 3: Create `context/conventions.md`**

```markdown
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
```

- [ ] **Step 4: Create `context/agent-capabilities.md`**

```markdown
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
```

- [ ] **Step 5: Create `scripts/post-install.sh`**

```bash
#!/bin/bash
set -e

AGENTS_DIR=".github/agents"

echo "Initializing GitHub AI agents structure..."

if [ ! -d "$AGENTS_DIR" ]; then
    mkdir -p "$AGENTS_DIR"
    echo "Created $AGENTS_DIR for reusable prompt files."
else
    echo "$AGENTS_DIR already exists, skipping creation."
fi

echo "github-ai-agents module setup complete."
```

- [ ] **Step 6: Create `scripts/agents-init.sh`**

```bash
#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")/templates"
WORKFLOWS_DIR="${PWD}/.github/workflows"
DOCS_DIR="${PWD}/docs"

force=false
if [[ "${1:-}" == "--force" ]]; then
    force=true
fi

echo "=== GitHub AI Agents Setup ==="
echo "Select an agent to scaffold:"
echo "  1) Claude Code Action (@claude mention handler)"
echo "  2) Codex / generic agent workflow"
echo "  3) PR reviewer (label-gated)"
echo "  4) All three + AGENT_PERMISSIONS.md policy doc"
read -p "Selection (1-4): " CHOICE

mkdir -p "$WORKFLOWS_DIR"

copy_template() {
    local src="$1"
    local dst="$2"
    mkdir -p "$(dirname "$dst")"
    if [ -f "$dst" ] && [ "$force" != "true" ]; then
        read -p "$dst already exists. Overwrite? (y/N) " OW
        [[ ! "$OW" =~ ^[Yy]$ ]] && { echo "Skipping $dst."; return; }
    fi
    if [ ! -f "$src" ]; then
        echo "ERROR: template not found at $src" >&2
        exit 1
    fi
    cp "$src" "$dst"
    echo "Created $dst"
}

add_claude() {
    copy_template "$TEMPLATE_DIR/claude-code-action.yml.tmpl" "$WORKFLOWS_DIR/claude-code.yml"
}
add_codex() {
    copy_template "$TEMPLATE_DIR/codex-action.yml.tmpl" "$WORKFLOWS_DIR/codex-action.yml"
}
add_reviewer() {
    copy_template "$TEMPLATE_DIR/agent-pr-review.yml.tmpl" "$WORKFLOWS_DIR/agent-pr-review.yml"
}
add_policy() {
    mkdir -p "$DOCS_DIR"
    copy_template "$TEMPLATE_DIR/AGENT_PERMISSIONS.md.tmpl" "$DOCS_DIR/AGENT_PERMISSIONS.md"
}

case "$CHOICE" in
    1) add_claude ;;
    2) add_codex ;;
    3) add_reviewer ;;
    4) add_claude; add_codex; add_reviewer; add_policy ;;
    *) echo "Invalid selection." >&2; exit 1 ;;
esac

echo "Done. Remember to set the required secrets (e.g., ANTHROPIC_API_KEY) in repo settings."
```

- [ ] **Step 7: Create `templates/claude-code-action.yml.tmpl`**

```yaml
# Triggers on @claude mentions in issues or PRs.
# Requires repo secret: ANTHROPIC_API_KEY
name: claude-code

on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
  issues:
    types: [opened, assigned]

permissions:
  contents: read
  pull-requests: write
  issues: write

concurrency:
  group: claude-${{ github.event.issue.number || github.event.pull_request.number }}
  cancel-in-progress: false

jobs:
  claude:
    if: contains(github.event.comment.body, '@claude') || contains(github.event.issue.body, '@claude')
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - name: Run Claude Code Action
        uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          # Optional: pin a prompt file for consistent behavior
          # prompt_file: .github/agents/code-reviewer.md
```

- [ ] **Step 8: Create `templates/codex-action.yml.tmpl`**

```yaml
# Generic agent workflow — adapt the `uses:` to your chosen agent action.
# Requires repo secret: OPENAI_API_KEY (or equivalent)
name: codex-agent

on:
  issue_comment:
    types: [created]

permissions:
  contents: read
  pull-requests: write
  issues: write

concurrency:
  group: codex-${{ github.event.issue.number }}
  cancel-in-progress: false

jobs:
  codex:
    if: contains(github.event.comment.body, '/codex')
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - name: Run Codex agent
        # Replace with the actual action for your chosen agent.
        run: |
          echo "Wire your agent invocation here."
          echo "API key available via OPENAI_API_KEY secret."
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

- [ ] **Step 9: Create `templates/agent-pr-review.yml.tmpl`**

```yaml
# Label-gated PR review by an AI agent.
# Add the `agent:review` label to a PR to trigger.
name: agent-pr-review

on:
  pull_request:
    types: [labeled]

permissions:
  contents: read
  pull-requests: write

concurrency:
  group: agent-review-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  review:
    if: github.event.label.name == 'agent:review'
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - name: Run agent reviewer
        uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          mode: review
```

- [ ] **Step 10: Create `templates/AGENT_PERMISSIONS.md.tmpl`**

```markdown
# Agent Permissions Policy

This document records which AI agents this repository invites, the GitHub permissions they hold, and the rationale.

## Agents

### claude-code (Anthropic)
- **Trigger:** `@claude` mention in issues or PR comments.
- **Permissions:** `contents: read`, `pull-requests: write`, `issues: write`.
- **Secrets used:** `ANTHROPIC_API_KEY`.
- **Rationale:** Enables Claude to read repo state and comment on issues/PRs. No write access to `contents:` — Claude cannot push directly.

### codex / generic agent
- **Trigger:** `/codex` comment.
- **Permissions:** `contents: read`, `pull-requests: write`, `issues: write`.
- **Secrets used:** `OPENAI_API_KEY` (or equivalent).
- **Rationale:** Read-only repo access plus issue/PR commenting.

### agent-pr-review
- **Trigger:** `agent:review` label applied to a PR.
- **Permissions:** `contents: read`, `pull-requests: write`.
- **Rationale:** Posts review comments only; cannot push or merge.

## Review Cadence
This file should be reviewed quarterly, or whenever an agent's permissions block is changed.
```

- [ ] **Step 11: Make scripts executable and run the test for this module**

```bash
chmod +x modules/deployment/github-ai-agents/scripts/post-install.sh
chmod +x modules/deployment/github-ai-agents/scripts/agents-init.sh
uv run pytest tests/unit/test_github_modules.py -v -k github-ai-agents
```

Expected: The three `github-ai-agents` parametrized cases pass.

- [ ] **Step 12: Commit**

```bash
git add modules/deployment/github-ai-agents/
git commit -m "feat(modules): add github-ai-agents module for AI agent workflows on github"
```

---

### Task 4: Build `github-bots` Module

**Files:**
- Create: `modules/deployment/github-bots/b1-module.yaml`
- Create: `modules/deployment/github-bots/context/best-practices.md`
- Create: `modules/deployment/github-bots/context/conventions.md`
- Create: `modules/deployment/github-bots/context/agent-capabilities.md`
- Create: `modules/deployment/github-bots/scripts/post-install.sh`
- Create: `modules/deployment/github-bots/scripts/bots-init.sh`
- Create: `modules/deployment/github-bots/templates/dependabot.yml.tmpl`
- Create: `modules/deployment/github-bots/templates/release-please.yml.tmpl`
- Create: `modules/deployment/github-bots/templates/triage-labeler.yml.tmpl`

- [ ] **Step 1: Create the manifest**

Create `modules/deployment/github-bots/b1-module.yaml`:

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

- [ ] **Step 2: Create `context/best-practices.md`**

```markdown
# GitHub Bots: Best Practices

## Identity
- **Prefer GitHub Apps over PATs.** Apps have scoped permissions, installation tokens that expire, and clear audit-log attribution.
- **Never run bots as a real user's PAT.** When the user leaves, every bot they ran silently breaks — and their personal access traces every automated action.
- **Give each bot its own GitHub App.** One app per responsibility: `release-bot`, `triage-bot`, `dependency-bot`. Don't grant a single app the union of all needed permissions.

## Permissions
- **Start from zero scopes and add only what's needed.** A labeler bot needs `issues: write` and `pull-requests: write` — nothing more.
- **Restrict app installation to the repos that need it.** Org-wide installation should be rare and reviewed.

## Audit
- Tag all bot-authored commits/PRs with a label (`bot:<name>`) so they are filterable.
- Review the org audit log quarterly for unexpected bot activity.

## Failure Modes
- **Set bot workflows to fail loudly.** A silently broken dependabot is worse than no dependabot — it gives false assurance.
- **Test bot changes in a fork or non-default branch first.** A misconfigured labeler can spam every open issue.
```

- [ ] **Step 3: Create `context/conventions.md`**

```markdown
# GitHub Bots: Conventions

## File Layout
```
.github/
├── dependabot.yml                # Dependabot ecosystem config
├── labeler.yml                   # actions/labeler path rules
└── workflows/
    ├── release-please.yml        # googleapis/release-please-action
    └── triage-labeler.yml        # actions/labeler workflow
```

## Label Taxonomy
- **Type:** `type:bug`, `type:feature`, `type:docs`, `type:refactor`
- **Area:** `area:cli`, `area:server`, `area:dashboard`, `area:modules`
- **Bot:** `bot:dependabot`, `bot:release-please`, `bot:triage`

## Dependabot Cadence
- Critical ecosystems (npm, pip with security advisories): `weekly`.
- Slower-moving ecosystems (docker base images, github-actions): `monthly`.
- Group patch-level updates to reduce PR noise: `groups:` with `update-types: [patch]`.

## Release-Please
- Use conventional commits (`feat:`, `fix:`, `chore:`) to drive version bumps.
- Pin `release-please-action` to a specific commit SHA, not a tag.
```

- [ ] **Step 4: Create `context/agent-capabilities.md`**

```markdown
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
```

- [ ] **Step 5: Create `scripts/post-install.sh`**

```bash
#!/bin/bash
set -e

GH_DIR=".github"

echo "Initializing GitHub bots structure..."

if [ ! -d "$GH_DIR" ]; then
    mkdir -p "$GH_DIR/workflows"
    echo "Created $GH_DIR/."
else
    echo "$GH_DIR already exists, skipping creation."
fi

echo "github-bots module setup complete."
```

- [ ] **Step 6: Create `scripts/bots-init.sh`**

```bash
#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")/templates"
GH_DIR="${PWD}/.github"
WORKFLOWS_DIR="${GH_DIR}/workflows"

force=false
if [[ "${1:-}" == "--force" ]]; then
    force=true
fi

echo "=== GitHub Bots Setup ==="
echo "Select a bot to scaffold:"
echo "  1) Dependabot (.github/dependabot.yml)"
echo "  2) release-please (.github/workflows/release-please.yml)"
echo "  3) Triage labeler (.github/workflows/triage-labeler.yml + .github/labeler.yml)"
echo "  4) All three"
read -p "Selection (1-4): " CHOICE

mkdir -p "$WORKFLOWS_DIR"

copy_template() {
    local src="$1"
    local dst="$2"
    mkdir -p "$(dirname "$dst")"
    if [ -f "$dst" ] && [ "$force" != "true" ]; then
        read -p "$dst already exists. Overwrite? (y/N) " OW
        [[ ! "$OW" =~ ^[Yy]$ ]] && { echo "Skipping $dst."; return; }
    fi
    if [ ! -f "$src" ]; then
        echo "ERROR: template not found at $src" >&2
        exit 1
    fi
    cp "$src" "$dst"
    echo "Created $dst"
}

add_dependabot() {
    copy_template "$TEMPLATE_DIR/dependabot.yml.tmpl" "$GH_DIR/dependabot.yml"
}
add_release_please() {
    copy_template "$TEMPLATE_DIR/release-please.yml.tmpl" "$WORKFLOWS_DIR/release-please.yml"
}
add_triage() {
    copy_template "$TEMPLATE_DIR/triage-labeler.yml.tmpl" "$WORKFLOWS_DIR/triage-labeler.yml"
    # Also drop a starter labeler.yml the workflow expects
    if [ ! -f "$GH_DIR/labeler.yml" ] || [ "$force" = "true" ]; then
        cat > "$GH_DIR/labeler.yml" <<'EOF'
# actions/labeler v5 config. Edit to match your repo's areas.
area:docs:
  - changed-files:
      - any-glob-to-any-file: ['docs/**', '**/*.md']
area:tests:
  - changed-files:
      - any-glob-to-any-file: ['tests/**']
EOF
        echo "Created $GH_DIR/labeler.yml"
    fi
}

case "$CHOICE" in
    1) add_dependabot ;;
    2) add_release_please ;;
    3) add_triage ;;
    4) add_dependabot; add_release_please; add_triage ;;
    *) echo "Invalid selection." >&2; exit 1 ;;
esac

echo "Done."
```

- [ ] **Step 7: Create `templates/dependabot.yml.tmpl`**

```yaml
version: 2
updates:
  # Python (uv / pip). Adjust directory if pyproject.toml lives elsewhere.
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    groups:
      python-patches:
        update-types: ["patch"]

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"

  # Docker base images
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "monthly"

  # Uncomment if you have a Node/JS package:
  # - package-ecosystem: "npm"
  #   directory: "/dashboard"
  #   schedule:
  #     interval: "weekly"
```

- [ ] **Step 8: Create `templates/release-please.yml.tmpl`**

```yaml
# Drives semver releases from conventional commits.
# See https://github.com/googleapis/release-please for config options.
name: release-please

on:
  push:
    branches: [main]

permissions:
  contents: write
  pull-requests: write

jobs:
  release-please:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v4
        with:
          # Pin to a SHA in production for supply-chain safety.
          release-type: python
          # config-file: release-please-config.json
          # manifest-file: .release-please-manifest.json
```

- [ ] **Step 9: Create `templates/triage-labeler.yml.tmpl`**

```yaml
# Auto-labels PRs based on file paths in .github/labeler.yml.
name: triage-labeler

on:
  pull_request_target:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/labeler@v5
        with:
          repo-token: ${{ secrets.GITHUB_TOKEN }}
          configuration-path: .github/labeler.yml
```

- [ ] **Step 10: Make scripts executable and run the test for this module**

```bash
chmod +x modules/deployment/github-bots/scripts/post-install.sh
chmod +x modules/deployment/github-bots/scripts/bots-init.sh
uv run pytest tests/unit/test_github_modules.py -v -k github-bots
```

Expected: The three `github-bots` parametrized cases pass.

- [ ] **Step 11: Commit**

```bash
git add modules/deployment/github-bots/
git commit -m "feat(modules): add github-bots module for dependabot/release-please/triage"
```

---

### Task 5: Run Full Test Suite and Integration Smoke Test

**Files:**
- Modify: none (verification + final commit only)

- [ ] **Step 1: Run the full unit-test suite to confirm green and no regressions**

Run: `uv run pytest tests/unit/ -v`
Expected: All previously-passing tests still pass; the 9 new `test_github_modules` cases all pass.

- [ ] **Step 2: Integration smoke — install one module into a tempdir and verify `b1 pair` picks it up**

This step verifies the *installer + compiler + translator* pipeline end-to-end against one of the new modules. It is a manual smoke for now — not added to the test suite — because the existing test suite already covers each component in isolation.

```bash
# From b1CodingTool/
TMPDIR_TEST=$(mktemp -d)
cd "$TMPDIR_TEST"
uv --project "$OLDPWD" run b1 init .
uv --project "$OLDPWD" run b1 install "$OLDPWD/modules/deployment/github-ai-agents"
uv --project "$OLDPWD" run b1 pair
grep -q "GitHub AI Agents" CLAUDE.md && echo "PASS: CLAUDE.md references the new module" || echo "FAIL: module context missing from CLAUDE.md"
cd "$OLDPWD"
rm -rf "$TMPDIR_TEST"
```

Expected: `PASS: CLAUDE.md references the new module`. If FAIL, inspect the `.agent/modules/github-ai-agents/` tree in the tempdir to check whether the install copied context files correctly.

- [ ] **Step 3: Update the ClickUp task to "in progress" or "complete"**

This is the human-facing closeout. The implementing engineer should update [ClickUp 86b9zfzxv](https://app.clickup.com/t/86b9zfzxv) status to reflect completion.

- [ ] **Step 4: Confirm git log is clean and commits tell the story**

Run: `git log --oneline -8`
Expected output should show the four feature commits plus the test commit, in roughly this order (newest first):

```
<sha> feat(modules): add github-bots module for dependabot/release-please/triage
<sha> feat(modules): add github-ai-agents module for AI agent workflows on github
<sha> feat(modules): add github-runners module for self-hosted runner setup
<sha> test: add failing manifest+artifact tests for github tool base modules
<sha> docs: add design spec for github tool base module expansion
```

If any commit message is off or any task's files leaked into the wrong commit, use `git rebase -i` to fix BEFORE pushing. (Only rewrite history that has not been pushed.)

- [ ] **Step 5: (Optional) Open a PR**

```bash
git push -u origin <branch-name>
# Then use the existing /commit-push-pr flow or `gh pr create` to open a PR.
```

---

## Self-review

**Spec coverage check:** Every section of the spec is covered:
- Three module dirs under `modules/deployment/` → Tasks 2, 3, 4.
- Manifests parse via `ModuleConfig.from_yaml` → Task 1 test enforces this.
- Three context files per module → Tasks 2/3/4 Steps 2–4.
- Working `*-init.sh` + ≥2 templates per module → Tasks 2/3/4 Steps 6–10 (varies).
- `uv run pytest` passes → Task 5 Step 1.
- `b1 install ... && b1 pair` references the new module in `CLAUDE.md` → Task 5 Step 2 smoke.
- Spec committed + plan committed at the documented path → already done for the spec; plan being saved now.

**Placeholder check:** No TBDs. Every YAML/markdown/bash artifact is shown in full. The only "replace with your build steps" string is inside the *runner workflow template* — that is the template's intended use (it is a starter for downstream users), not a plan placeholder.

**Type consistency:** All slash command prefixes match across the manifest, the `agent-capabilities.md`, and the test parametrization (`/gh-runners`, `/gh-agents`, `/gh-bots`). Script filenames match between manifest hooks (`scripts/post-install.sh`) and what's created. Test file paths match what each task creates.
