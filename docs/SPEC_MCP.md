# SPEC_MCP: Model Context Protocol Integration

## 1. Objective

Standardize the interaction between agentic coding platforms (Claude Code, Gemini CLI, Codex) and the `b1CodingTool` ecosystem. Transition from static file synchronization to a dynamic, two-way protocol that allows agents to manage their own environment context and tools.

## 2. Core Components

### 2.1 MCP Server Implementation

* **Framework**: Utilize the official `mcp` Python SDK.
* **Integration**: The MCP server will reside in `src/b1/server/mcp_server.py` and run alongside the existing FastAPI dashboard.
* **Transport**: Support standard `stdio` for local agent integration (e.g., Claude Desktop/Code) and `SSE` for the web dashboard.

## 3. Tool Definitions

Coding agents should be able to execute core `b1` operations via standard MCP tools, wrapping existing `typer` logic.

| Tool Name | CLI Equivalent | Description |
| --- | --- | --- |
| `b1_init` | `b1 init` | Initializes a new or existing project with the `b1` structure. |
| `b1_install` | `b1 install <module>` | Fetches and mounts a "superpower" module into the project. |
| `b1_pair` | `b1 pair` | Synchronizes the centralized `agent.md` context across agent-specific files. |
| `b1_link_github` | `b1 link-github` | Connects a project to a remote repository for version control syncing. |
| `b1_link_clickup` | `b1 link-clickup` | Maps a project to a ClickUp list for real-time task context. |
| `b1_status` | N/A | Returns a JSON summary of installed modules and current context parity. |

## 4. Resource Schemas

Provide agents with on-demand access to project metadata and conventions without bloating the context window.

### 4.1 `b1://context/compiled`

* **Source**: Dynamically generated via the `compiler` logic.
* **Content**: The fully merged content of the project-level `agent.md` and all active module `context/` files.

### 4.2 `b1://modules/library`

* **Source**: `src/b1/core/fetcher.py` and local `modules/` directory.
* **Content**: A directory of available superpowers and their capabilities.

### 4.3 `b1://config/project`

* **Source**: `.b1/config.yaml` managed by the `config` core.
* **Content**: Project settings, linked integrations, and environment variables.

## 5. Use Cases for Agents

### 5.1 Autonomous Scaffolding

When an agent detects a new tech stack (e.g., SwiftUI), it should call `b1_install language/swift` to instantly align the project with preferred directory structures and best practices.

### 5.2 Context Refreshing

After updating project-wide rules in `agent.md`, the agent can trigger `b1_pair` via MCP to ensure its own `CLAUDE.md` or `GEMINI.md` is instantly synchronized.

### 5.3 Live Task Integration

Agents can query linked ClickUp lists as an MCP resource to determine the next relevant task or to update task status upon successful implementation.

## 6. Implementation Roadmap

1. **Dependency Injection**: Add `mcp >= 0.1.0` to `pyproject.toml`.
2. **Server Scaffold**: Create `src/b1/server/mcp_server.py` using the `FastMCP` class.
3. **Tool Mapping**: Wrap existing `typer` command logic into MCP tool handlers.
4. **Agent Integration**: Configure `claude_desktop_config.json` to point to the local `b1` installation.
5. **Parity Testing**: Verify that `b1 pair` executed via MCP correctly updates all target files.