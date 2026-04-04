# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**b1CodingTool** is an agent-agnostic development environment manager that standardizes AI coding assistant workflows (Claude Code, Gemini CLI, Codex, etc.). It provides a Python CLI and a local React dashboard to manage agent context, module-based skills, and project-specific tooling.

The project is currently in **specification phase** — `docs/SPEC.md` is the authoritative design document. No implementation code exists yet.

## Planned Tech Stack

- **CLI & Core Logic:** Python, managed via `uv`
- **Backend (Dashboard API):** FastAPI or standard Python HTTP server
- **Frontend Dashboard:** React (served on localhost)

## Implementation Phases (from SPEC.md)

1. **Phase 1:** Python project init via `uv`; implement `b1 init` with safe merge/append to existing `agent.md` files
2. **Phase 2:** Module schema (JSON/YAML); `b1 install` command; skillsmp.com community skill integration
3. **Phase 3:** `b1 pull` / `b1 push` with automated PR creation via git library
4. **Phase 4:** React frontend + local FastAPI server for dashboard

## Core Architecture

### CLI Commands (to be implemented)
| Command | Purpose |
|---|---|
| `b1 init` | Scaffold `.agent/` and `docs/` directories; generate hierarchical `agent.md` files |
| `b1 install <module>` | Download and mount a module's skills, commands, context, and hooks |
| `b1 pull` | Sync local modules with upstream |
| `b1 push` | Draft a PR to contribute project-agnostic learnings back to the central repo |
| `b1 dashboard` | Start the local HTTP server and React frontend |

### Module System
Each module encapsulates framework-specific or domain-specific context:
```
module-name/
├── skills/      # Reusable agent tasks/functions
├── commands/    # Custom slash commands (e.g., /setup-flutter-bloc)
├── hooks/       # Scripts run before/after agent actions
└── context/     # Markdown files injected into agent knowledge base
```

Module categories: **Cross-Cutting** (general best practices), **Development** (framework-specific: React, Flutter, Django, FastAPI), **Deployment** (cloud/app store targets: AWS, Apple App Store).

### Context Manager (`agent.md` hierarchy)
`b1 init` creates a two-level agent context system:
- **Root `agent.md`:** Project-agnostic software development practices
- **`project/agent.md`:** App logic, directory structures, active tasks

The `b1 init` implementation must safely merge into existing `agent.md` files without destroying current data.

### Project Scaffold (created by `b1 init`)
```
project-root/
├── .agent/
│   ├── agent.md          # Root agent guidelines
│   └── project/
│       └── agent.md      # Project-specific context
├── docs/
└── README.md
```

### Dashboard Views
- **Module Explorer:** Browse/install/uninstall modules
- **Skill Inspector:** View active skills and custom commands
- **Resource Manager:** Secure API key storage
- **Telemetry/Session Monitor:** Track agent usage and token consumption
