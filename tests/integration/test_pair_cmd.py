# tests/integration/test_pair_cmd.py
from pathlib import Path
from typer.testing import CliRunner
from b1.cli import app

runner = CliRunner()


def test_pair_writes_agent_files(cd_project):
    result = runner.invoke(app, ["pair"])
    assert result.exit_code == 0
    assert (cd_project / "CLAUDE.md").exists()
    assert (cd_project / "GEMINI.md").exists()
    assert (cd_project / "CODEX.md").exists()


def test_pair_content_includes_root_context(cd_project):
    runner.invoke(app, ["pair"])
    content = (cd_project / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Global Context" in content


def test_pair_content_includes_project_context(cd_project):
    runner.invoke(app, ["pair"])
    content = (cd_project / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Project Context" in content


def test_pair_content_includes_installed_module_context(make_project, make_module, monkeypatch):
    module = make_module(name="django", context_files={"best-practices.md": "# Django best practices\n"})
    project = make_project()
    monkeypatch.chdir(project)

    from unittest.mock import patch
    with patch("b1.commands.install.ModuleFetcher") as MockFetcher:
        MockFetcher.return_value.fetch.return_value = module
        runner.invoke(app, ["install", str(module)])

    runner.invoke(app, ["pair"])
    content = (project / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Django best practices" in content


def test_pair_files_contain_auto_generation_warning(cd_project):
    runner.invoke(app, ["pair"])
    content = (cd_project / "CLAUDE.md").read_text(encoding="utf-8")
    assert "AUTO-GENERATED" in content


def test_pair_exits_with_error_outside_initialized_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["pair"])
    assert result.exit_code != 0
