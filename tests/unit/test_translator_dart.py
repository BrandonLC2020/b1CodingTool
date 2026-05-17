from pathlib import Path
from b1.core.translator import AgentTranslator

COMPILED_DART = "<!-- b1CodingTool: Module Context [dart] - conventions.md -->\n# Dart Rules\nUse camelCase."

def test_claude_dart_context_formatting(tmp_path):
    AgentTranslator(tmp_path).generate_files(["CLAUDE"], COMPILED_DART)
    # The translator creates .claude/context/dart/conventions.md
    # Based on the current implementation of _get_file_info:
    # 'Module Context [dart] - conventions.md' -> ('dart', 'conventions.md')
    content = (tmp_path / ".claude" / "context" / "dart" / "conventions.md").read_text()
    assert "<dart_context>" in content
    assert "Use camelCase." in content
