# b1CodingTool: Phase 1 Implementation Plan

## Goal Description

The goal is to complete **Phase 1: CLI Foundation & Context Management** as specified in `SPEC.md`. This involves bootstrapping the Python project using `uv`, setting up the core CLI architecture with Typer and Rich, and implementing the `b1 init` command to scaffold `.agent/`, `docs/`, and hierarchical `agent.md` context files safely.

## Important Notes & Review Needed
> [!IMPORTANT]
> - **Project Initialization**: I plan to use `uv init` in the current root to set up `pyproject.toml` and standard package structure (`src/b1`). Are you okay with the default `uv init` structure?
> - **Agent.md Merging Strategy**: The spec mentions safely merging or appending to existing `agent.md` files. For Phase 1, I propose appending new standardized sections to the end of existing files (if the file exists but lacks b1 headers) to prevent data destruction. Will this be sufficient for the initial implementation?

---

## Proposed Changes

### Project Foundation
- Use `uv init` to bootstrap the `pyproject.toml`.
- Add `typer` and `rich` as main dependencies (`uv add typer rich`).

### `b1` Core Package
#### [NEW] `src/b1/cli.py`
- Main Typer application entry point.
- Configures global Rich console formatting.

#### [NEW] `src/b1/__main__.py`
- Allows module execution via `python -m b1`.

#### [MODIFY] `pyproject.toml`
- Add entry point configuration mapping `b1` to `b1.cli:app` executable.

---

### Core CLI Implementation
#### [NEW] `src/b1/commands/init.py`
- Code for the `b1 init` command to trigger the scaffolding logic.

#### [NEW] `src/b1/core/scaffolder.py`
- Business logic to safely create `.agent/` and `docs/` directories.
- Generate standard `.gitignore` and `README.md` if they do not exist.

#### [NEW] `src/b1/core/context_manager.py`
- Handles the safe creation and merging of hierarchical `agent.md` context files.
- Establishes `agent.md` at project root.
- Establishes a template `.agent/project/agent.md` sub-context file.
- Logic to ensure existing files are appended to (or preserved) rather than completely overwritten.

---

## Open Questions
> [!NOTE]
> - Should the Typer app be explicitly named something like `b1` in the `--help` outputs?
> - For the `pyproject.toml`, what should the versioning format be? (e.g., standard SemVer `0.1.0`)
> - Will the CLI be published to PyPI later, or is it strictly for local/workspace installation?

---

## Verification Plan

### Automated Tests
- We will add testing (e.g., with `pytest`) to assert file creation logic without full file replacement.

### Manual Verification
- Manually trigger `uv run b1 init` inside a clean test folder and verify the correct directory tree.
- Modify the generated `agent.md`, run `b1 init` again, and verify that existing data wasn't overwritten or destroyed.
