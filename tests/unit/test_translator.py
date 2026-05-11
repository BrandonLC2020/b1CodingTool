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


def test_generates_filemap_and_hidden_dirs(tmp_path):
    AgentTranslator(tmp_path).generate_files(["CLAUDE", "GEMINI"], COMPILED)
    
    # Root filemaps should exist
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / "GEMINI.md").exists()
    
    # Hidden dirs should exist
    assert (tmp_path / ".claude").is_dir()
    assert (tmp_path / ".gemini").is_dir()
    
    # Individual context files should exist
    assert (tmp_path / ".claude" / "root_context.md").exists()
    assert (tmp_path / ".claude" / "project_context.md").exists()
    assert (tmp_path / ".gemini" / "root_context.md").exists()
    assert (tmp_path / ".gemini" / "project_context.md").exists()


def test_claude_filemap_and_content(tmp_path):
    AgentTranslator(tmp_path).generate_files(["CLAUDE"], COMPILED)
    
    # Filemap check
    root_content = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert ".claude/root_context.md" in root_content
    assert ".claude/project_context.md" in root_content
    assert "instructions" in root_content.lower() or "read" in root_content.lower()
    
    # Content check
    section_content = (tmp_path / ".claude" / "root_context.md").read_text(encoding="utf-8")
    assert "<root_context>" in section_content
    assert "# Global Context" in section_content


def test_gemini_filemap_and_content(tmp_path):
    AgentTranslator(tmp_path).generate_files(["GEMINI"], COMPILED)
    
    # Filemap check
    root_content = (tmp_path / "GEMINI.md").read_text(encoding="utf-8")
    assert ".gemini/root_context.md" in root_content
    
    # Content check
    section_content = (tmp_path / ".gemini" / "root_context.md").read_text(encoding="utf-8")
    assert "You are a Gemini CLI agent" in section_content
    assert "## Root Context" in section_content


def test_codex_filemap_and_content(tmp_path):
    AgentTranslator(tmp_path).generate_files(["CODEX"], COMPILED)
    
    # Filemap check
    root_content = (tmp_path / "CODEX.md").read_text(encoding="utf-8")
    assert ".codex/root_context.md" in root_content
    
    # Content check
    section_content = (tmp_path / ".codex" / "root_context.md").read_text(encoding="utf-8")
    assert "<!-- b1CodingTool" not in section_content
    assert "# Global Context" in section_content
