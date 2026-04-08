# tests/slow/test_push_real_git.py
"""
Tests that make real git calls against a local repo. Run with: pytest -m slow
`gh pr create` and `git push` (no remote configured) are mocked.
"""
import subprocess
import subprocess as real_subprocess
import yaml
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from b1.cli import app

runner = CliRunner()

# Keep a hard reference to the real subprocess.run before any patching
_real_run = subprocess.run


def _init_git_repo(path: Path):
    _real_run(["git", "init", str(path)], check=True, capture_output=True)
    _real_run(["git", "-C", str(path), "config", "user.email", "test@test.com"], check=True, capture_output=True)
    _real_run(["git", "-C", str(path), "config", "user.name", "Test"], check=True, capture_output=True)
    # Initial commit so branch operations work
    (path / "README.md").write_text("init\n", encoding="utf-8")
    _real_run(["git", "-C", str(path), "add", "."], check=True, capture_output=True)
    _real_run(["git", "-C", str(path), "commit", "-m", "init"], check=True, capture_output=True)


@pytest.mark.slow
def test_push_creates_branch_and_stages_agent_dir(tmp_path, monkeypatch, make_project):
    project = make_project(upstream_repo="org/repo")
    _init_git_repo(project)
    # Add a new file to .agent/ AFTER the initial commit so there are staged changes
    (project / ".agent" / "project" / "new-context.md").write_text("# New Context\n", encoding="utf-8")
    monkeypatch.chdir(project)

    def selective_run(cmd, *args, **kwargs):
        """Pass git calls through to real subprocess; mock gh and git push (no remote)."""
        if isinstance(cmd, list) and cmd[0] == "gh":
            m = MagicMock()
            m.stdout = "https://github.com/org/repo/pull/1"
            m.returncode = 0
            return m
        if isinstance(cmd, list) and cmd[:2] == ["git", "push"]:
            # No remote configured in tmp repo — mock the push to avoid CalledProcessError
            m = MagicMock()
            m.returncode = 0
            m.stdout = ""
            m.stderr = b""
            return m
        # Use the captured real subprocess.run to avoid recursion through the mock
        return _real_run(cmd, *args, **kwargs)

    with patch("b1.commands.push.shutil.which", return_value="/usr/bin/gh"):
        with patch("b1.commands.push.subprocess.run", side_effect=selective_run):
            result = runner.invoke(app, ["push"])

    # Verify a b1-learnings-* branch exists in the real git repo
    branches = _real_run(
        ["git", "-C", str(project), "branch"],
        capture_output=True, text=True
    ).stdout
    assert "b1-learnings-" in branches, (
        f"Expected b1-learnings-* branch, got: {branches!r}\n"
        f"CLI exit code: {result.exit_code}\n"
        f"CLI output: {result.output}"
    )
