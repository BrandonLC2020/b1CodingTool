# Implement link-to-github-repo command Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a CLI command `link-to-github-repo` to link a b1 project to a GitHub repository and persist the owner, repo name, and default branch in the project config.

**Architecture:** Use regex for ID extraction, verify existence via `gh` CLI (primary) or `git ls-remote` (fallback), and update `B1Config`.

**Tech Stack:** Python, Typer, Pydantic, YAML, `gh` CLI, `git`.

---

### Task 1: Update B1Config Schema

**Files:**
- Modify: `src/b1/core/config.py`
- Test: `tests/unit/test_config.py`

- [ ] **Step 1: Write failing test for config updates**

```python
def test_config_serialization_with_github_fields():
    from b1.core.config import B1Config
    config = B1Config(
        github_owner="brandon",
        github_repo="b1CodingTool",
        default_branch="main"
    )
    dump = config.model_dump()
    assert dump["github_owner"] == "brandon"
    assert dump["github_repo"] == "b1CodingTool"
    assert dump["default_branch"] == "main"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_config.py -v`
Expected: FAIL (ValidationError or fields missing)

- [ ] **Step 3: Add fields to B1Config**

```python
class B1Config(BaseModel):
    upstream_repo: str = ""
    active_agents: List[str] = Field(default_factory=list)
    clickup_list_id: Optional[str] = None
    github_owner: Optional[str] = None
    github_repo: Optional[str] = None
    default_branch: Optional[str] = None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_config.py -v`

- [ ] **Step 5: Commit**

```bash
git add src/b1/core/config.py tests/unit/test_config.py
git commit -m "feat(config): add github metadata fields to B1Config"
```

---

### Task 2: Implement Extraction Logic

**Files:**
- Create: `src/b1/commands/link_github.py`
- Create: `tests/unit/test_link_github.py`

- [ ] **Step 1: Write tests for ID extraction**

```python
import pytest
from b1.commands.link_github import extract_github_slug

@pytest.mark.parametrize("input_str,expected", [
    ("https://github.com/owner/repo", ("owner", "repo")),
    ("git@github.com:owner/repo.git", ("owner", "repo")),
    ("owner/repo", ("owner", "repo")),
    ("https://github.com/owner/repo.git", ("owner", "repo")),
    ("invalid", None),
])
def test_extract_github_slug(input_str, expected):
    assert extract_github_slug(input_str) == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/unit/test_link_github.py -v`
Expected: FAIL (Module not found)

- [ ] **Step 3: Implement extraction regex**

```python
import re

def extract_github_slug(input_str: str) -> tuple[str, str] | None:
    pattern = r"(?:github\.com[:/]|)([\w.-]+)/([\w.-]+?)(?:\.git|/|$)"
    match = re.search(pattern, input_str)
    if match:
        return match.group(1), match.group(2)
    return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/unit/test_link_github.py -v`

- [ ] **Step 5: Commit**

```bash
git add src/b1/commands/link_github.py tests/unit/test_link_github.py
git commit -m "feat(github): implement github slug extraction"
```

---

### Task 3: Implement Verification and Command

**Files:**
- Modify: `src/b1/commands/link_github.py`
- Modify: `src/b1/cli.py`
- Create: `tests/integration/test_link_github_cmd.py`

- [ ] **Step 1: Write integration test with mocked verification**

```python
from typer.testing import CliRunner
from b1.cli import app
from unittest.mock import patch
import json

runner = CliRunner()

def test_link_github_cmd_success(tmp_path):
    with patch("b1.commands.link_github.subprocess.run") as mock_run:
        # Mock gh success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({
            "owner": {"login": "brandon"},
            "name": "b1CodingTool",
            "defaultBranchRef": {"name": "main"}
        })
        
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["link-to-github-repo", "owner/repo"])
            assert result.exit_code == 0
            assert "Success" in result.stdout
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/integration/test_link_github_cmd.py -v`
Expected: FAIL (Command not found)

- [ ] **Step 3: Implement command and register it**

In `src/b1/commands/link_github.py`:
```python
import subprocess
import json
import typer
from b1.core.config import B1Config
from rich.console import Console
from pathlib import Path

console = Console()

def link_github_cmd(input_str: str):
    slug = extract_github_slug(input_str)
    if not slug:
        console.print("[red]Error: Invalid GitHub URL or slug.[/red]")
        raise typer.Exit(1)
    
    owner, repo = slug
    console.print(f"Verifying [blue]{owner}/{repo}[/blue]...")
    
    # Try gh
    try:
        res = subprocess.run(
            ["gh", "repo", "view", f"{owner}/{repo}", "--json", "owner,name,defaultBranchRef"],
            capture_output=True, text=True
        )
        if res.returncode == 0:
            data = json.loads(res.stdout)
            owner = data["owner"]["login"]
            repo = data["name"]
            branch = data["defaultBranchRef"]["name"]
        else:
            # Fallback to git
            res = subprocess.run(["git", "ls-remote", "--get-url", f"https://github.com/{owner}/{repo}"], capture_output=True)
            if res.returncode != 0:
                raise Exception("Repo not found")
            branch = "main"
    except Exception:
        console.print("[red]Error: Could not verify repository existence.[/red]")
        raise typer.Exit(1)

    config = B1Config.load(Path.cwd())
    config.github_owner = owner
    config.github_repo = repo
    config.default_branch = branch
    config.upstream_repo = f"{owner}/{repo}"
    config.save(Path.cwd())
    console.print(f"[green]Success! Linked to {owner}/{repo} (branch: {branch})[/green]")
```

Register in `src/b1/cli.py`.

- [ ] **Step 4: Run integration tests**

- [ ] **Step 5: Commit**

```bash
git add src/b1/commands/link_github.py src/b1/cli.py tests/integration/test_link_github_cmd.py
git commit -m "feat(cli): implement and register link-to-github-repo command"
```

---

### Task 4: Update Agent Context Injection

**Files:**
- Modify: `src/b1/core/compiler.py`

- [ ] **Step 1: Update compiler to include github metadata**

- [ ] **Step 2: Verify by running `b1 pair` in a mock project**

- [ ] **Step 3: Commit**

```bash
git commit -am "feat(compiler): include github metadata in agent context"
```
