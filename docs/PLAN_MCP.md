# b1CodingTool: Model Context Protocol (MCP) Integration Plan

## Goal Description

The goal is to implement the Model Context Protocol (MCP) as specified in `docs/SPEC_MCP.md`. This will transition `b1CodingTool` from static file synchronization to a dynamic, two-way protocol. Agents (like Claude Code, Gemini CLI, and Cursor) will be able to interact with the project context, install modules, and synchronize configurations through a standardized set of tools and resources.

## Important Notes & Review Needed
> [!IMPORTANT]
> - **SDK Choice**: I will use the official `mcp` Python SDK (FastMCP) for implementation.
> - **Dual Transport**: The server needs to handle `stdio` for local CLI agents and `SSE` for the web dashboard. I'll focus on `stdio` first as the primary use case for coding agents.
> - **Typer Integration**: Since `b1` uses `typer`, the MCP tools should ideally invoke the same underlying core logic used by the CLI commands to ensure behavior parity.

---

## Proposed Changes

### Infrastructure & Setup
- Add `mcp` and `uvicorn` (for SSE support) to `pyproject.toml`.
- Configure `src/b1/server/mcp_server.py` as the entry point for the MCP server.

### Core Implementation
#### [NEW] `src/b1/server/mcp_server.py`
- Initialize `FastMCP("b1")`.
- Implement `stdio` transport handling.
- Placeholder for `SSE` transport (to be integrated with FastAPI if needed).

#### [NEW] Tool Mappings
- `b1_init`: Wraps logic from `src/b1/commands/init.py`.
- `b1_install`: Wraps logic from `src/b1/commands/install.py`.
- `b1_pair`: Wraps logic from `src/b1/commands/pair.py`.
- `b1_link_github`: Wraps logic from `src/b1/commands/link_github.py`.
- `b1_link_clickup`: Wraps logic from `src/b1/commands/link_clickup.py`.
- `b1_status`: New logic to return JSON summary of project state.

#### [NEW] Resource Definitions
- `b1://context/compiled`: Returns the output of `ContextCompiler.compile()`.
- `b1://modules/library`: Returns a list of available modules from `Fetcher`.
- `b1://config/project`: Returns the current `.agent/config.yaml` as JSON.

---

### Refactoring for Reusability
- Ensure `src/b1/commands/*.py` logic is decoupled from `typer` contexts where possible, moving core logic to `src/b1/core/` to make it easily callable by both the CLI and MCP server.

---

## Open Questions
> [!NOTE]
> - Should we package the MCP server as a separate entry point in `pyproject.toml` (e.g., `b1-mcp`)?
> - For `b1_install`, how should we handle the interactive/shell hooks that might be defined in modules when called via MCP?
> - Do we want to support any custom prompt templates via MCP?

---

## Verification Plan

### Automated Tests
- Create `tests/integration/test_mcp_server.py`.
- Mock agent requests to verify tool execution and resource retrieval.
- Assert that `b1_pair` via MCP produces the same file output as `b1 pair` via CLI.

### Manual Verification
- Configure a local `claude_desktop_config.json` to use the `b1` MCP server.
- Verify tools are visible and functional in Claude Desktop.
- Query resources and verify the returned context matches the project state.
