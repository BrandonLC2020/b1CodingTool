# b1CodingTool: Phase 4 Implementation Plan

## Goal Description
Implement the `b1 pair` command. This command acts as a context compiler, traversing the hierarchical `b1CodingTool` architectures (root `agent.md`, project `agent.md`, and module contexts) to build and sync standard configuration files (`CLAUDE.md`, `GEMINI.md`, `CODEX.md`) that natively control differing assistant behaviors inside an IDE.

## Important Notes & Review Needed
> [!IMPORTANT]
> **Generation Scope**:
> Should `b1 pair` simply stitch the `agent.md` texts together exactly as they are and copy them over, or should it wrap them in provider-specific xml tags? (For example, Claude loves `<system_instructions>` tags).
>
> **Which Agents**:
> Currently, the spec mentions `CLAUDE.md`, `CODEX.md`, and `GEMINI.md`. Do you want it to output all three by default when `b1 pair` is run, or should the user configure which ones they want active?

---

## Proposed Changes

### Context Compiler
#### [NEW] `src/b1/core/compiler.py`
- Create a `ContextCompiler` class that scans the project to aggregate content:
  1. Reads `agent.md` at the root.
  2. Reads `.agent/project/agent.md`.
  3. Iterates through `.agent/modules/*/context/` to append relevant installed rulesets.
- Concatenates the instructions into a unified string.

### Output Translator
#### [NEW] `src/b1/core/translator.py`
- Contains mapping configurations for different providers natively supported by IDEs.
- `translator.generate("CLAUDE", context_str)` -> Wraps context appropriately and writes to `CLAUDE.md` in the root.
- Handles generation for `GEMINI.md` and `CODEX.md`.

### Command Logic
#### [NEW] `src/b1/commands/pair.py`
#### [MODIFY] `src/b1/cli.py` (Add `pair` command)
- Implements `b1 pair`.
- Executes the compiler mapping, translates, and writes the output files locally.

## Verification Plan
### Manual Testing
- Create diverse instructions.
- Run `uv run b1 pair`.
- Verify the physical generation of `CLAUDE.md` and `GEMINI.md`.
