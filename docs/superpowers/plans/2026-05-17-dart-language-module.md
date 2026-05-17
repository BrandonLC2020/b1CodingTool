# Dart Language Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a first-class Dart language module with automated skills, context guidelines, and core CLI enhancements for intelligent agentic workflows.

**Architecture:** We will create a new development module in `modules/language/dart` and extend the Python core (`rule_extractor.py` and `translator.py`) to natively support Dart syntax, markers, and specialized formatting for agents like Claude.

**Tech Stack:** Python (Core CLI), Dart (Module Target), Shell (Hooks)

---

### Task 1: Module Structure & Manifest

**Files:**
- Create: `modules/language/dart/b1-module.yaml`
- Create: `modules/language/dart/context/.gitkeep` (temp to ensure directory exists)

- [ ] **Step 1: Create the directory structure**

Run: `mkdir -p modules/language/dart/context modules/language/dart/scripts modules/language/dart/templates`

- [ ] **Step 2: Create the `b1-module.yaml` manifest**

```yaml
name: dart
version: 1.0.0
type: development
description: "Core Dart language standards, sound null-safety, and modern pub ecosystem guidelines."
skills:
  - name: "Dart Test Generator"
    description: "Automated generation of package:test suites for Dart classes and functions."
  - name: "Pub Dependency Manager"
    description: "Assists in adding, removing, and upgrading dependencies via pub.dev."
  - name: "Sealed Class Refactor"
    description: "Refactor class hierarchies to use Dart 3+ sealed classes for exhaustive switching."
hooks:
  post-install: "scripts/post-install.sh"
```

- [ ] **Step 3: Commit**

```bash
git add modules/language/dart/b1-module.yaml
git commit -m "feat(dart): add module manifest and structure"
```

---

### Task 2: Core CLI Enhancement: Rule Extractor

**Files:**
- Modify: `src/b1/core/rule_extractor.py`
- Create: `tests/unit/test_rule_extractor_dart.py`

- [ ] **Step 1: Write the failing test for Dart markers**

```python
# tests/unit/test_rule_extractor_dart.py
from b1.core.rule_extractor import RuleExtractor

def test_extract_dart_markers():
    content = """
    void main() {
      // b1:generalized:start
      // Always use sealed classes for state.
      // b1:generalized:end
      print('hello');
    }
    """
    rules = RuleExtractor().extract(content)
    assert "Always use sealed classes for state." in rules
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_rule_extractor_dart.py -v`
Expected: FAIL (rules will be empty)

- [ ] **Step 3: Implement Dart marker support in `RuleExtractor`**

```python
# src/b1/core/rule_extractor.py
import re
from typing import List

class RuleExtractor:
    # Existing MARKER_REGEX (HTML style)
    MARKER_REGEX = re.compile(
        r"<!-- b1:generalized:start -->\s*(.*?)\s*<!-- b1:generalized:end -->", 
        re.DOTALL
    )
    
    # NEW: Dart/C-style marker support
    DART_MARKER_REGEX = re.compile(
        r"// b1:generalized:start\s*(.*?)\s*// b1:generalized:end",
        re.DOTALL
    )
    
    FALLBACK_HEADER = "## Generalized Learnings"
    
    def extract(self, content: str) -> List[str]:
        rules = []
        
        # Try HTML markers first
        matches = self.MARKER_REGEX.findall(content)
        if matches:
            rules.extend([m.strip() for m in matches])
            
        # Try Dart/C-style markers
        dart_matches = self.DART_MARKER_REGEX.findall(content)
        if dart_matches:
            # Clean up the leading '// ' from each line in the match
            for match in dart_matches:
                cleaned = "\n".join([line.strip().lstrip("//").strip() for line in match.splitlines()])
                rules.append(cleaned.strip())
                
        if rules:
            return rules
            
        # Fallback to header... (existing logic)
        if self.FALLBACK_HEADER in content:
            start_index = content.find(self.FALLBACK_HEADER)
            section_content = content[start_index + len(self.FALLBACK_HEADER):].strip()
            next_header_match = re.search(r"\n##\s+", section_content)
            if next_header_match:
                section_content = section_content[:next_header_match.start()].strip()
            if section_content:
                rules.append(section_content)
                
        return rules
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_rule_extractor_dart.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/b1/core/rule_extractor.py tests/unit/test_rule_extractor_dart.py
git commit -m "feat(core): support Dart-style rule extraction markers"
```

---

### Task 3: Core CLI Enhancement: Agent Translator

**Files:**
- Modify: `src/b1/core/translator.py`
- Create: `tests/unit/test_translator_dart.py`

- [ ] **Step 1: Write failing test for Dart-specific Claude formatting**

```python
# tests/unit/test_translator_dart.py
from pathlib import Path
from b1.core.translator import AgentTranslator

COMPILED_DART = "<!-- b1CodingTool: Module Context [dart] - conventions.md -->\n# Dart Rules\nUse camelCase."

def test_claude_dart_context_formatting(tmp_path):
    AgentTranslator(tmp_path).generate_files(["CLAUDE"], COMPILED_DART)
    content = (tmp_path / ".claude" / "context" / "dart" / "conventions.md").read_text()
    assert "<dart_context>" in content
    assert "Use camelCase." in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_translator_dart.py -v`
Expected: FAIL (will likely have `<module_context_dart___conventions_md>` instead)

- [ ] **Step 3: Implement specialized Dart formatting in `AgentTranslator`**

```python
# src/b1/core/translator.py
# (Locate _format_section and modify)

    def _format_section(self, agent: str, name: str, body: str) -> str:
        """Formats a single section based on the target agent."""
        if agent == "CLAUDE":
            # Specialized formatting for Dart module
            if "[dart]" in name.lower():
                return f"<dart_context>\n{body}\n</dart_context>"
            
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

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_translator_dart.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/b1/core/translator.py tests/unit/test_translator_dart.py
git commit -m "feat(core): specialized Claude formatting for Dart context"
```

---

### Task 4: Context Files: Conventions & Modern Dart

**Files:**
- Create: `modules/language/dart/context/conventions.md`
- Create: `modules/language/dart/context/modern-dart.md`

- [ ] **Step 1: Create `conventions.md`**

```markdown
# Dart: Coding Conventions

## Naming Standards
- **Classes, Enums, Typedefs, Type Parameters:** `PascalCase`.
- **Libraries, Packages, Directories, Source Files:** `snake_case`.
- **Variables, Parameters, Named Parameters, Constants:** `camelCase`.
- **Private Members:** Prefix with an underscore `_`.

## Formatting
- **Standard:** Use `dart format .` exclusively.
- **Line Length:** 80 characters.
- **Indentation:** 2 spaces.

## Best Practices
- **Prefer `final`:** Use `final` for variables that aren't reassigned.
- **Arrow Syntax:** Use `=>` for single-line functions or getters.
- **Strings:** Use adjacent string literals for concatenation, not `+`.
```

- [ ] **Step 2: Create `modern-dart.md`**

```markdown
# Modern Dart (3.x+) Guidelines

## Pattern Matching & Records
- **Records:** Use for multiple return values: `(double lat, double lon) getLocation()`.
- **Destructuring:** Use pattern matching to unpack records: `var (lat, lon) = getLocation();`.

## Sealed Hierarchies
- **Sealed Classes:** Use `sealed` for Restricted Class Hierarchies (e.g., UI States).
- **Exhaustive Switches:** Leverage compiler-checked exhaustive switching on sealed types.

## Null Safety
- **Soundness:** Assume code is soundly null-safe.
- **Avoid `!`:** Prefer `if (x != null)` or `??` over the bang operator.
- **Late:** Use `late` only when initialization is guaranteed before first access.
```

- [ ] **Step 3: Commit**

```bash
git add modules/language/dart/context/conventions.md modules/language/dart/context/modern-dart.md
git commit -m "docs(dart): add conventions and modern dart context"
```

---

### Task 5: Context Files: Dependencies & Testing

**Files:**
- Create: `modules/language/dart/context/dependency-management.md`
- Create: `modules/language/dart/context/testing.md`

- [ ] **Step 1: Create `dependency-management.md`**

```markdown
# Dart: Dependency Management (Pub)

## pubspec.yaml
- **Environment:** Always pin the lower bound of the SDK: `sdk: ">=3.3.0 <4.0.0"`.
- **Dependencies:** Use `dependencies:` for runtime and `dev_dependencies:` for tools/tests.

## Versioning
- **Caret Syntax:** Use `^1.2.3` for semantic version compatibility.
- **Overrides:** Use `dependency_overrides:` sparingly for local path debugging.

## Commands
- `dart pub get`: Fetch dependencies.
- `dart pub upgrade`: Upgrade dependencies to latest within constraints.
- `dart pub outdated`: Check for updateable packages.
```

- [ ] **Step 2: Create `testing.md`**

```markdown
# Dart: Testing Standards

## Setup
- **Directory:** All tests must reside in the `test/` folder.
- **Naming:** Files must end in `_test.dart`.

## Framework (package:test)
- **Grouping:** Use `group()` to organize related tests.
- **Assertions:** Use `expect(actual, matcher)`.
- **Async:** Use `testWidgets` for UI or `test(...) async` for logic.

## Mocking
- **Preferred:** Use `mocktail` for type-safe mocking without code generation.
- **Fakes:** Prefer simple `Fake` class implementations for data repositories.
```

- [ ] **Step 3: Commit**

```bash
git add modules/language/dart/context/dependency-management.md modules/language/dart/context/testing.md
git commit -m "docs(dart): add dependency and testing context"
```

---

### Task 4: Automation: post-install script

**Files:**
- Create: `modules/language/dart/scripts/post-install.sh`

- [ ] **Step 1: Create `post-install.sh`**

```bash
#!/bin/bash
# modules/language/dart/scripts/post-install.sh

if [ -f "pubspec.yaml" ]; then
    echo "Dart project detected. Resolving dependencies..."
    if command -v flutter &> /dev/null && grep -q "sdk: flutter" pubspec.yaml; then
        flutter pub get
    else
        dart pub get
    fi
fi
```

- [ ] **Step 2: Make it executable**

Run: `chmod +x modules/language/dart/scripts/post-install.sh`

- [ ] **Step 3: Commit**

```bash
git add modules/language/dart/scripts/post-install.sh
git commit -m "feat(dart): add post-install hook for dependency resolution"
```

---

### Task 5: Final Verification & Installation

- [ ] **Step 1: Verify the module manifest**

Run: `uv run python -m b1 install modules/language/dart --link`

- [ ] **Step 2: Verify `agent.md` compilation**

Run: `uv run python -m b1 pair`
Expected: `CLAUDE.md`, `GEMINI.md`, etc., should now contain Dart context links.

- [ ] **Step 3: Verify specialized Claude formatting**

Run: `cat .claude/context/dart/conventions.md`
Expected: Output should be wrapped in `<dart_context>` tags.

- [ ] **Step 4: Commit all final changes**

```bash
git add .
git commit -m "feat(dart): complete dart language module implementation"
```
