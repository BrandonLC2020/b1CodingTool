# tests/unit/test_translator.py
from pathlib import Path
from b1.core.translator import AgentTranslator

COMPILED = "# Global Context\nSome content here.\n"


def test_generates_file_for_each_agent(tmp_path):
    AgentTranslator(tmp_path).generate_files(["CLAUDE", "GEMINI"], COMPILED)
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / "GEMINI.md").exists()


def test_filenames_are_uppercased(tmp_path):
    AgentTranslator(tmp_path).generate_files(["claude"], COMPILED)
    assert (tmp_path / "CLAUDE.md").exists()


def test_files_contain_compiled_content(tmp_path):
    AgentTranslator(tmp_path).generate_files(["CLAUDE"], COMPILED)
    content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "Global Context" in content
    assert "Some content here." in content


def test_files_contain_auto_generation_warning(tmp_path):
    AgentTranslator(tmp_path).generate_files(["CLAUDE"], COMPILED)
    content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "AUTO-GENERATED" in content


def test_overwrites_existing_file(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("old content", encoding="utf-8")
    AgentTranslator(tmp_path).generate_files(["CLAUDE"], COMPILED)
    content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "old content" not in content
    assert "Global Context" in content


def test_empty_agents_list_writes_no_files(tmp_path):
    AgentTranslator(tmp_path).generate_files([], COMPILED)
    assert list(tmp_path.glob("*.md")) == []
