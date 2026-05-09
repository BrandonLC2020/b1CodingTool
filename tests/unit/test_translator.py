# tests/unit/test_translator.py
from pathlib import Path
from b1.core.translator import AgentTranslator

COMPILED = """
<!-- b1CodingTool: Root Context -->
# Global Context
Some content here.

<!-- b1CodingTool: Project Context -->
# Project specific
App logic.
"""


def test_generates_file_for_each_agent(tmp_path):
    AgentTranslator(tmp_path).generate_files(["CLAUDE", "GEMINI"], COMPILED)
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / "GEMINI.md").exists()


def test_claude_contains_xml_tags(tmp_path):
    AgentTranslator(tmp_path).generate_files(["CLAUDE"], COMPILED)
    content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "<project_context>" in content
    assert "<root_context>" in content
    assert "<project_context>" in content
    assert "# Global Context" in content


def test_gemini_contains_preamble(tmp_path):
    AgentTranslator(tmp_path).generate_files(["GEMINI"], COMPILED)
    content = (tmp_path / "GEMINI.md").read_text(encoding="utf-8")
    assert "You are a Gemini CLI agent" in content
    assert "## Root Context" in content


def test_codex_is_clean_markdown(tmp_path):
    AgentTranslator(tmp_path).generate_files(["CODEX"], COMPILED)
    content = (tmp_path / "CODEX.md").read_text(encoding="utf-8")
    assert "<!-- b1CodingTool" not in content
    assert "# Global Context" in content
