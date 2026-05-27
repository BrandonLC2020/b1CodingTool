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
