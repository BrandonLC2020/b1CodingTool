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
