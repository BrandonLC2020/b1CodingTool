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
