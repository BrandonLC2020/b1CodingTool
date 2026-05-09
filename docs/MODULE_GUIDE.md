# b1 Module Authoring Guide

This guide explains how to create, structure, and distribute modules for the **b1CodingTool**. Modules are the primary way to package framework-specific context, agent skills, and automation for AI coding assistants.

---

## 1. Overview
A module is a collection of guidelines and tools that enhance an AI agent's ability to work within a specific domain (e.g., a language, framework, or deployment platform).

### Module Types
- **Cross-Cutting**: General best practices (e.g., Clean Architecture, Security).
- **Development**: Framework-specific tools (e.g., Flutter, Django, React).
- **Deployment**: Infrastructure and CI/CD tools (e.g., AWS, GitHub Actions).

---

## 2. Anatomy of a Module
A standard module follows this directory structure:

```text
my-module/
├── b1-module.yaml      # REQUIRED: The module manifest
├── context/            # REQUIRED: Markdown files for agent memory
│   └── main.md         # Domain-specific instructions
├── skills/             # OPTIONAL: Reusable agent tasks
│   └── setup-db.md     # Task-specific instructions
├── commands/           # OPTIONAL: Slash command documentation
├── scripts/            # OPTIONAL: Supporting shell scripts
└── templates/          # OPTIONAL: Scaffolding files
```

---

## 3. Sourcing and Installation
Modules can be installed from two primary sources:

### Local Installation
Use a local path for active development:
```bash
uv run b1 install /path/to/my-module --link
```
The `--link` flag creates a symlink, allowing you to edit the module in its source repository and see changes immediately in your project.

### Remote Installation
Install from a Git repository:
```bash
uv run b1 install https://github.com/username/my-module.git
```
Remote modules are cached in `~/.b1/cache/`.

---

## 4. The Manifest (`b1-module.yaml`)
The `b1-module.yaml` file defines the module's identity and capabilities.

### Minimal Example
```yaml
name: my-cool-framework
version: 1.0.0
type: development
description: "Guidelines and tools for MyCoolFramework."
```

### Full Schema
| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | String | Unique identifier (alphanumeric, underscores, hyphens). |
| `version` | String | Semantic version (e.g., 1.2.3). |
| `type` | Enum | `cross_cutting`, `development`, or `deployment`. |
| `description`| String | A brief summary of the module's purpose. |
| `skills` | List | Reusable agent tasks (see below). |
| `commands` | List | Custom slash commands (see below). |
| `hooks` | Dict | Lifecycle scripts (e.g., `post-install`). |

---

## 5. Features in Detail

### Context (`context/`)
Files in the `context/` directory are automatically compiled into the `agent.md` hierarchy when you run `b1 pair`. These files should contain high-level rules, architecture patterns, and "gotchas" for the domain.

### Skills (`skills/`)
Skills are specific, reusable tasks. You can define them in the manifest to trigger setup scripts:

```yaml
skills:
  - name: "Database Migrator"
    description: "Sets up and runs initial migrations."
    install_command: "bash scripts/setup_db.sh"
```
The `install_command` runs during `b1 install`.

### Commands (`commands/`)
Commands document custom slash commands for the agent. While the CLI doesn't execute these directly, they are compiled into the agent's instructions so the assistant knows how to respond to them.

```yaml
commands:
  - name: "/api-gen"
    description: "Generate a new API endpoint"
    usage: "/api-gen <endpoint-name> --async"
```

### Hooks (`hooks/`)
Hooks allow you to run automation at specific points in the module lifecycle. Currently, `post-install` is the primary supported hook.

```yaml
hooks:
  post-install: "scripts/setup.sh"
```
The script is executed relative to the project root after the module files have been copied or linked.

---

## 6. Best Practices
1. **Be Surgical**: Only include context that is strictly necessary for the domain.
2. **Use Relative Paths**: In your manifest, always use relative paths for scripts.
3. **Idempotent Hooks**: Ensure your `post-install` scripts can be run multiple times without causing errors.
4. **Document Commands**: Provide clear usage examples for your slash commands.
5. **Version Semantically**: Update the version number in `b1-module.yaml` whenever you make breaking changes to the context or scripts.

---

## 7. Example Module Walkthrough
Check out the `modules/framework/django-ninja/` directory in the core repository for a real-world example of a development module with skills, commands, and hooks.
