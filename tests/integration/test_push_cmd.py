# tests/integration/test_push_cmd.py
import subprocess
from unittest.mock import patch, MagicMock, call
from typer.testing import CliRunner
from b1.cli import app

runner = CliRunner()

# push.py uses `import subprocess` and `import shutil` at top level,
# so the correct mock targets are:
_MOCK_RUN = "b1.commands.push.subprocess.run"
_MOCK_WHICH = "b1.commands.push.shutil.which"


def _successful_run(returncode=0, stdout="", stderr=b""):
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    m.stderr = stderr
    return m


def test_push_exits_with_error_outside_initialized_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["push"])
    assert result.exit_code != 0


def test_push_exits_with_error_when_gh_not_installed(cd_project):
    with patch(_MOCK_WHICH, return_value=None):
        result = runner.invoke(app, ["push"])
    assert result.exit_code != 0


def test_push_creates_branch_with_correct_prefix(make_project, monkeypatch):
    project = make_project(upstream_repo="org/repo")
    monkeypatch.chdir(project)

    # status --porcelain returns staged files (non-empty → proceed with commit)
    status_mock = MagicMock(stdout=".agent/config.yaml M\n", returncode=0)

    with patch(_MOCK_WHICH, return_value="/usr/bin/gh"):
        with patch(_MOCK_RUN) as mock_run:
            mock_run.side_effect = [
                _successful_run(),           # git checkout -b
                _successful_run(),           # git add .agent/
                status_mock,                 # git status --porcelain
                _successful_run(),           # git commit
                _successful_run(),           # git push
                _successful_run(stdout="https://github.com/org/repo/pull/1"),  # gh pr create
            ]
            runner.invoke(app, ["push"])

    branch_call = mock_run.call_args_list[0][0][0]
    assert branch_call[:3] == ["git", "checkout", "-b"]
    assert branch_call[3].startswith("b1-learnings-")


def test_push_returns_cleanly_when_no_changes_to_stage(make_project, monkeypatch):
    project = make_project(upstream_repo="org/repo")
    monkeypatch.chdir(project)

    empty_status = MagicMock(stdout="", returncode=0)

    with patch(_MOCK_WHICH, return_value="/usr/bin/gh"):
        with patch(_MOCK_RUN) as mock_run:
            mock_run.side_effect = [
                _successful_run(),   # git checkout -b
                _successful_run(),   # git add .agent/
                empty_status,        # git status --porcelain (no changes)
                _successful_run(),   # git checkout -
                _successful_run(),   # git branch -d
            ]
            result = runner.invoke(app, ["push"])

    assert result.exit_code == 0
    # gh pr create should NOT have been called
    calls_args = [c[0][0] for c in mock_run.call_args_list if c[0]]
    assert not any("gh" in str(a) for a in calls_args)
