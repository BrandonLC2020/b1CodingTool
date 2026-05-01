# Design Doc: link-to-github-repo Command

## Overview
The `link-to-github-repo` command establishes a verified connection between a `b1` project and its GitHub repository. By persisting metadata like owner, repository name, and default branch, it provides high-signal context to agentic workers (e.g., Gemini CLI, Claude Code), enabling them to use GitHub-specific tools autonomously and accurately.

## Problem Statement
Coding agents often have to infer the repository location or ask for confirmation before using GitHub MCP or CLI tools. This creates friction and potential for error, especially in workspaces with multiple remotes or complex naming conventions.

## Success Criteria
- Users can run `b1 link-to-github-repo <url_or_slug>`.
- The command parses `owner/repo` from common GitHub URL formats and raw slugs.
- The command verifies the repository's existence and accessibility.
- Metadata (`github_owner`, `github_repo`, `default_branch`) is persisted in `.agent/config.yaml`.
- The `upstream_repo` field is standardized to `owner/repo` and synced.
- The metadata is included in the compiled agent context (GEMINI.md, etc.) during `b1 pair`.

## Architecture

### 1. Configuration Schema (`src/b1/core/config.py`)
Add the following optional fields to `B1Config`:
- `github_owner: Optional[str] = None`
- `github_repo: Optional[str] = None`
- `default_branch: Optional[str] = None`

### 2. Command Logic (`src/b1/commands/link_github.py`)
- **Extraction:** Use regex to handle:
    - `https://github.com/owner/repo`
    - `git@github.com:owner/repo.git`
    - `owner/repo`
  Regex: `(?:github\.com[:/]|)([\w.-]+)/([\w.-]+?)(?:\.git|/|$)`
- **Verification:**
    - **Primary (`gh`):** `gh repo view <owner>/<repo> --json owner,name,defaultBranchRef`
    - **Fallback (`git`):** `git ls-remote --get-url https://github.com/<owner>/<repo>`
- **Persistence:** Update `B1Config` and save to `.agent/config.yaml`.

### 3. Agent Context Integration (`src/b1/core/compiler.py`)
Ensure that `ContextCompiler` includes this GitHub metadata in the generated context files so agents know they have verified GitHub access.

## Data Flow
1. **Input:** User runs `b1 link-to-github-repo <input>`.
2. **Parse:** Extract `owner` and `repo` using regex.
3. **Verify:**
    - Call `gh repo view`. If successful, use the returned `owner.login`, `name`, and `defaultBranchRef.name`.
    - If `gh` fails, call `git ls-remote`. If successful, set `github_owner` and `github_repo` from the parse step and default `default_branch` to `main`.
4. **Update:** 
    - Set `config.github_owner`, `config.github_repo`, `config.default_branch`.
    - Set `config.upstream_repo = f"{github_owner}/{github_repo}"`.
5. **Save:** Write config to `.agent/config.yaml`.

## Testing Plan

### Unit Tests (`tests/unit/test_link_github.py`)
- Test `extract_github_slug` against various URL/slug formats.
- Test `B1Config` field additions and persistence.

### Integration Tests (`tests/integration/test_link_github_cmd.py`)
- Mock `subprocess.run` to simulate `gh` and `git` command outputs.
- Verify CLI command correctly updates `.agent/config.yaml`.
- Verify error cases (invalid slug, repository not found).
