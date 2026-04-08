# tests/unit/test_context_manager.py
from pathlib import Path
from b1.core.context_manager import setup_context


def _agent_dir(root: Path) -> Path:
    return root / ".agent" / "project"


def test_creates_root_agent_md_when_missing(tmp_path):
    setup_context(tmp_path)
    assert (tmp_path / "agent.md").exists()


def test_root_agent_md_contains_b1_marker(tmp_path):
    setup_context(tmp_path)
    content = (tmp_path / "agent.md").read_text(encoding="utf-8")
    assert "b1CodingTool" in content


def test_appends_to_existing_agent_md_without_marker(tmp_path):
    (tmp_path / "agent.md").write_text("# Existing content\n", encoding="utf-8")
    setup_context(tmp_path)
    content = (tmp_path / "agent.md").read_text(encoding="utf-8")
    assert "Existing content" in content
    assert "b1CodingTool" in content


def test_does_not_modify_agent_md_with_marker_already_present(tmp_path):
    original = "# b1CodingTool: Global Context\nAlready configured.\n"
    (tmp_path / "agent.md").write_text(original, encoding="utf-8")
    setup_context(tmp_path)
    assert (tmp_path / "agent.md").read_text(encoding="utf-8") == original


def test_creates_project_agent_md(tmp_path):
    setup_context(tmp_path)
    assert (tmp_path / ".agent" / "project" / "agent.md").exists()


def test_project_agent_md_contains_project_context_heading(tmp_path):
    setup_context(tmp_path)
    content = (tmp_path / ".agent" / "project" / "agent.md").read_text(encoding="utf-8")
    assert "Project Context" in content


def test_does_not_overwrite_existing_project_agent_md(tmp_path):
    proj_dir = tmp_path / ".agent" / "project"
    proj_dir.mkdir(parents=True)
    proj_md = proj_dir / "agent.md"
    proj_md.write_text("# Custom project context\n", encoding="utf-8")
    setup_context(tmp_path)
    assert proj_md.read_text(encoding="utf-8") == "# Custom project context\n"
