# Design Doc: link-to-github-repo Command

## Overview
The `link-to-github-repo` command establishes a verified connection between a `b1` project and its GitHub repository. By persisting metadata like owner, repository name, and default branch, it provides high-signal context to agentic workers (e.g., Gemini CLI, Claude Code), enabling them to use GitHub-specific tools autonomously and accurately.

## Problem Statement
Coding agents often have to infer the repository location or ask for confirmation before using GitHub MCP or CLI tools. This creates friction and potential for error, especially in workspaces with multiple remotes or complex naming conventions.

## Success Criteria
- Users can run `b1 link-to-github-repo <url_or_slug>`.
- The command parses `owner/repo` from common GitHub URL formats and raw slugs.
- The command verifies the repository's existence and accessibility via GitHub API/MCP.
- Metadata (`github_owner`, `github_repo`, `default_branch`) is persisted in `.agent/config.yaml`.
- The `upstream_repo` field is standardized to `owner/repo` and synced.
- The metadata is included in the compiled agent context (GEMINI.md, etc.) during `b1 pair`.

## Architecture

### 1. Configuration Schema (`src/b1/core/config.py`)
Add the following optional fields to `B1Config`:
- `github_owner: Optional[str]`
- `github_repo: Optional[str]`
- `default_branch: Optional[str]`

### 2. Command Logic (`src/b1/commands/link_github.py`)
- **Extraction:** Regex to handle formats like `https://github.com/owner/repo`, `git@github.com:owner/repo.git`, and `owner/repo`.
- **Verification:** Attempt to fetch repository details (specifically the default branch) using available GitHub tools.
- **Persistence:** Update `B1Config` and save to `.agent/config.yaml`.

### 3. Agent Context Integration (`src/b1/core/compiler.py`)
Ensure that `ContextCompiler` includes this GitHub metadata in the generated context files so agents know they have verified GitHub access.

## Implementation Details

### GitHub ID Extraction Pattern
Regex: `(?:github\\.com[:/]|)([\\w.-]+)/([\\w.-]+?)(?:\\.git|/|$)`

### Flow
1.  **Input:** User provides a URL or slug.
2.  **Parse:** Extract `owner` and `repo`.
3.  **Verify:** Call GitHub API to confirm access and retrieve the `default_branch`.
4.  **Configure:** 
    - Update `config.github_owner`, `config.github_repo`, and `config.default_branch`.
    - Set `config.upstream_repo = f"{owner}/{repo}"`.
5.  **Persist:** Save configuration.
6.  **Notify:** Print success with verified details.

## Testing Plan

### Unit Tests (`tests/unit/test_link_github.py`)
- Verify regex extraction against URLs (HTTPS/SSH) and raw slugs.
- Verify Pydantic model updates.

### Integration Tests (`tests/integration/test_link_github_cmd.py`)
- Mock GitHub verification responses.
- Verify filesystem updates to `.agent/config.yaml`.
- Verify that metadata appears in compiled `GEMINI.md` after a mock pair operation.
