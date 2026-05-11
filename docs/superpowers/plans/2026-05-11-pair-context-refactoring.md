# B1 Pair Context Refactoring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the `b1 pair` translator to generate lightweight root markdown files acting as filemaps, while writing the actual compiled context sections into per-agent hidden folders (`.claude/`, `.gemini/`, `.codex/`) to prevent context bloat.

**Architecture:** We will modify `AgentTranslator` in `src/b1/core/translator.py`. Instead of formatting the entire context string and writing it to `{AGENT}.md`, the translator will create a `.{agent.lower()}/` directory, iterate over the parsed sections, format each section, and write them to individual markdown files (e.g., `.claude/root_context.md`). It will then generate a lightweight `{AGENT}.md` root file containing instructions and relative paths pointing to the files in the hidden directory.

**Tech Stack:** Python, pytest, `pathlib.Path`, `re`.

---

### Task 1: Update Tests for AgentTranslator

**Files:**
- Modify: `tests/unit/test_translator.py`

- [ ] **Step 1: Write the failing tests**

Update `tests/unit/test_translator.py` to reflect the new expected behavior:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/unit/test_translator.py -v`
Expected: FAIL because `generate_files` still writes everything to the root file and doesn't create hidden directories.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_translator.py
git commit -m "test: update translator tests for hidden folders and filemap generation"
```

---

### Task 2: Implement Hidden Folder and Filemap Generation

**Files:**
- Modify: `src/b1/core/translator.py`

- [ ] **Step 1: Write the implementation**

Update `src/b1/core/translator.py` completely to this:

```python
import re
import shutil
from pathlib import Path
from rich.console import Console

console = Console()

class AgentTranslator:
    """
    Translates compiled context into agent-specific configuration files (CLAUDE.md, GEMINI.md, etc.)
    with tailored formatting for each provider, storing actual content in hidden directories.
    """
    
    SECTION_REGEX = re.compile(r"(<!-- b1CodingTool: (.*?) -->)", re.DOTALL)
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        
    def generate_files(self, agents: list[str], compiled_content: str):
        """
        Generates tailored markdown files and directory structures for each target agent.
        """
        header = "<!-- THIS FILE IS AUTO-GENERATED BY b1CodingTool (b1 pair). DO NOT EDIT DIRECTLY. -->\n\n"
        sections = self._parse_sections(compiled_content)
        
        for agent in agents:
            agent_upper = agent.upper()
            agent_lower = agent.lower()
            
            # Setup hidden directory
            hidden_dir_name = f".{agent_lower}"
            hidden_dir_path = self.project_dir / hidden_dir_name
            
            # Clean up old context dir if it exists
            if hidden_dir_path.exists():
                shutil.rmtree(hidden_dir_path)
            hidden_dir_path.mkdir(parents=True, exist_ok=True)
            
            filemap_links = []
            
            # Write individual section files
            for name, body in sections:
                safe_name = self._safe_filename(name)
                file_name = f"{safe_name}.md"
                file_path = hidden_dir_path / file_name
                
                formatted_body = self._format_section(agent_upper, name, body)
                file_path.write_text(formatted_body, encoding="utf-8")
                
                # Add to filemap list
                filemap_links.append(f"- [{name}]({hidden_dir_name}/{file_name})")
            
            # Generate the root filemap
            root_filename = f"{agent_upper}.md"
            out_path = self.project_dir / root_filename
            
            instructions = (
                f"# {agent_upper} Context Filemap\n\n"
                "To prevent context bloat, the full project and module contexts are not inlined here. "
                "Instead, they are available in the files linked below. "
                "**Please read these files when you need specific context.**\n\n"
            )
            
            final_root_content = header + instructions + "\n".join(filemap_links) + "\n"
            out_path.write_text(final_root_content, encoding="utf-8")
            
            console.print(f"[green]✔ Generated:[/green] {root_filename} and {hidden_dir_name}/")

    def _safe_filename(self, name: str) -> str:
        """Converts section name to safe filename (e.g. 'Root Context' -> 'root_context')"""
        safe = name.lower().replace(" ", "_").replace("[", "").replace("]", "").replace("-", "_").replace(".", "_")
        return re.sub(r"[^a-z0-9_]", "", safe)

    def _parse_sections(self, content: str):
        """Splits the compiled content into a list of (section_name, section_content) tuples."""
        sections = []
        matches = list(self.SECTION_REGEX.finditer(content))
        
        if not matches:
            return [("Context", content.strip())]
            
        for i, match in enumerate(matches):
            section_name = match.group(2).strip()
            start_pos = match.end()
            end_pos = matches[i+1].start() if i + 1 < len(matches) else len(content)
            section_content = content[start_pos:end_pos].strip()
            sections.append((section_name, section_content))
            
        return sections

    def _format_section(self, agent: str, name: str, body: str) -> str:
        """Formats a single section based on the target agent."""
        if agent == "CLAUDE":
            tag_name = self._safe_filename(name)
            return f"<{tag_name}>\n{body}\n</{tag_name}>"
            
        elif agent == "GEMINI":
            preamble = (
                "You are a Gemini CLI agent specializing in software engineering tasks. "
                "Follow the project conventions and architectural patterns defined below strictly."
            )
            return f"> [!IMPORTANT]\n> {preamble}\n\n## {name}\n{body}"
            
        elif agent == "CODEX":
            return self.SECTION_REGEX.sub("", body).strip()
            
        else:
            return body
```

- [ ] **Step 2: Run tests to verify they pass**

Run: `uv run pytest tests/unit/test_translator.py -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add src/b1/core/translator.py
git commit -m "feat(translator): generate hidden per-agent folders and root filemaps"
```
