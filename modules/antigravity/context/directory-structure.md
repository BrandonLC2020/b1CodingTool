# Antigravity: Directory Structure

## Agent Workspace
Antigravity manages missions and agents in an internal workspace, but interacts with the local file system through these artifacts:

```
.antigravity/ (Optional)
├── policies.json       # Workspace-specific agent execution policies
├── missions/           # History of implementation plans and walkthroughs
└── .antigravityignore  # Files and folders to exclude from agent context
```

## Standard Exclusions
Recommended `.antigravityignore` defaults:
```
# Dependency folders
node_modules/
.venv/
__pycache__/

# Build artifacts
dist/
build/
.next/
out/

# Secret protection
.env
.env.local
*.pem
*.key
```
