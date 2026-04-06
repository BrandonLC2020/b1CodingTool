# Test Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Parallelization note:** After Task 2 (conftest.py) is complete, Tasks 3–10 are fully independent and can run in parallel. After all unit tests pass, Tasks 11–16 are also independent and can run in parallel.

**Goal:** Build a full pytest test suite (unit + integration + slow/real-git) with shared fixtures that auto-construct project/module directory structures so individual tests need no manual filesystem setup.

**Architecture:** Three layers — unit tests call module functions directly against `tmp_path` fixtures; integration tests invoke CLI commands via `CliRunner` against real temp directories with `monkeypatch.chdir()`; slow tests run actual git commands in temp repos. All subprocess/git calls outside the `slow/` layer are mocked.

**Tech Stack:** pytest 8+, pytest-cov, httpx (FastAPI TestClient), unittest.mock (stdlib), typer.testing.CliRunner

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `pyproject.toml` | Add dev deps + pytest config |
| Create | `tests/__init__.py` | Make tests a package |
| Create | `tests/conftest.py` | `make_module`, `make_project`, `cd_project` fixtures |
| Create | `tests/unit/__init__.py` | Package marker |
| Create | `tests/unit/test_config.py` | B1Config load/save |
| Create | `tests/unit/test_schema.py` | ModuleConfig.from_yaml |
| Create | `tests/unit/test_scaffolder.py` | scaffold_project |
| Create | `tests/unit/test_context_manager.py` | setup_context |
| Create | `tests/unit/test_compiler.py` | ContextCompiler.compile |
| Create | `tests/unit/test_translator.py` | AgentTranslator.generate_files |
| Create | `tests/unit/test_fetcher.py` | ModuleFetcher.fetch (mocked subprocess) |
| Create | `tests/unit/test_installer.py` | ModuleInstaller.install |
| Create | `tests/integration/__init__.py` | Package marker |
| Create | `tests/integration/test_init_cmd.py` | `b1 init` end-to-end |
| Create | `tests/integration/test_install_cmd.py` | `b1 install` end-to-end |
| Create | `tests/integration/test_pair_cmd.py` | `b1 pair` end-to-end |
| Create | `tests/integration/test_pull_cmd.py` | `b1 pull` end-to-end |
| Create | `tests/integration/test_push_cmd.py` | `b1 push` end-to-end |
| Create | `tests/integration/test_server.py` | FastAPI endpoints |
| Create | `tests/slow/__init__.py` | Package marker |
| Create | `tests/slow/test_fetcher_real_git.py` | Real git clone/pull |
| Create | `tests/slow/test_push_real_git.py` | Real git branch/stage |

---

## Task 1: Add Dev Dependencies and Pytest Config

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add dev dependencies and pytest config to pyproject.toml**

Replace the `[build-system]` section (keep it) and add below the existing `[project]` block:

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "httpx>=0.27",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--tb=short"
markers = [
    "slow: tests that make real git/network calls (run with: pytest -m slow)",
]
```

- [ ] **Step 2: Install dev deps**

```bash
uv sync
```

Expected: resolves and installs pytest, pytest-cov, httpx with no errors.

- [ ] **Step 3: Create package markers**

```bash
mkdir -p tests/unit tests/integration tests/slow
touch tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py tests/slow/__init__.py
```

- [ ] **Step 4: Verify pytest is reachable**

```bash
uv run pytest --collect-only
```

Expected: `no tests ran` (no test files yet) with exit code 5 or 0 — no import errors.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml tests/
git commit -m "chore: add pytest dev dependencies and test directory structure"
```

---

## Task 2: Write conftest.py (Core Fixtures)

**Files:**
- Create: `tests/conftest.py`

- [ ] **Step 1: Write conftest.py**

```python
# tests/conftest.py
import shutil
import pytest
import yaml
from pathlib import Path


@pytest.fixture
def make_module(tmp_path):
    """
    Factory fixture. Returns a callable that creates a valid module source directory.

    Usage:
        module_dir = make_module()
        module_dir = make_module(name="django", context_files={"best-practices.md": "# tips"})
    """
    def _make(name="test-module", version="1.0.0", context_files=None):
        module_dir = tmp_path / "src_modules" / name
        module_dir.mkdir(parents=True, exist_ok=True)

        config = {
            "name": name,
            "version": version,
            "type": "development",
            "description": f"Test module: {name}",
            "skills": [],
            "hooks": {},
        }
        (module_dir / "b1-module.yaml").write_text(yaml.dump(config), encoding="utf-8")

        if context_files:
            ctx_dir = module_dir / "context"
            ctx_dir.mkdir(exist_ok=True)
            for filename, content in context_files.items():
                (ctx_dir / filename).write_text(content, encoding="utf-8")

        return module_dir

    return _make


@pytest.fixture
def make_project(tmp_path):
    """
    Factory fixture. Returns a callable that creates a fully scaffolded project directory.

    Usage:
        project = make_project()
        project = make_project(modules=["django"])
        project = make_project(agents=["CLAUDE", "GEMINI"], upstream_repo="org/repo")
    """
    def _make(agents=None, upstream_repo=None, modules=None):
        project_dir = tmp_path / "project"
        project_dir.mkdir(exist_ok=True)

        # .agent/ structure
        (project_dir / ".agent" / "project").mkdir(parents=True)
        (project_dir / ".agent" / "modules").mkdir(parents=True)

        # agent.md files
        (project_dir / "agent.md").write_text(
            "# b1CodingTool: Global Context\nRoot agent context.\n",
            encoding="utf-8",
        )
        (project_dir / ".agent" / "project" / "agent.md").write_text(
            "# b1CodingTool: Project Context\nProject-specific context.\n",
            encoding="utf-8",
        )

        # config.yaml
        config_data = {
            "upstream_repo": upstream_repo or "",
            "active_agents": agents or ["CLAUDE", "GEMINI", "CODEX"],
        }
        (project_dir / ".agent" / "config.yaml").write_text(
            yaml.dump(config_data), encoding="utf-8"
        )

        # Install named modules
        if modules:
            for name in modules:
                mod_dir = project_dir / ".agent" / "modules" / name
                (mod_dir / "context").mkdir(parents=True)
                (mod_dir / "b1-module.yaml").write_text(
                    yaml.dump({
                        "name": name,
                        "version": "1.0.0",
                        "type": "development",
                        "description": f"Test {name} module",
                        "skills": [],
                        "hooks": {},
                    }),
                    encoding="utf-8",
                )

        return project_dir

    return _make


@pytest.fixture
def cd_project(make_project, monkeypatch):
    """
    Creates a default scaffolded project and chdirs into it.
    The original working directory is restored automatically after the test.

    Usage:
        def test_something(cd_project):
            # Path.cwd() is now the temp project dir
            result = runner.invoke(app, ["pair"])
    """
    project_dir = make_project()
    monkeypatch.chdir(project_dir)
    return project_dir
```

- [ ] **Step 2: Verify fixtures are importable**

```bash
uv run pytest --collect-only
```

Expected: no errors, `conftest.py` loaded silently.

- [ ] **Step 3: Commit**

```bash
git add tests/conftest.py
git commit -m "test: add make_module, make_project, and cd_project fixtures"
```

---

## Task 3: Unit Tests — config.py

**Files:**
- Create: `tests/unit/test_config.py`

- [ ] **Step 1: Write tests**

```python
# tests/unit/test_config.py
import yaml
import pytest
from pathlib import Path
from b1.core.config import B1Config


def test_load_returns_empty_config_when_file_missing(tmp_path):
    config = B1Config.load(tmp_path)
    assert config.upstream_repo == ""
    assert config.active_agents == []


def test_load_deserializes_valid_yaml(tmp_path):
    (tmp_path / ".agent").mkdir()
    (tmp_path / ".agent" / "config.yaml").write_text(
        yaml.dump({"upstream_repo": "https://github.com/org/repo", "active_agents": ["CLAUDE"]}),
        encoding="utf-8",
    )
    config = B1Config.load(tmp_path)
    assert config.upstream_repo == "https://github.com/org/repo"
    assert config.active_agents == ["CLAUDE"]


def test_load_handles_empty_yaml_file(tmp_path):
    (tmp_path / ".agent").mkdir()
    (tmp_path / ".agent" / "config.yaml").write_text("", encoding="utf-8")
    config = B1Config.load(tmp_path)
    assert config.upstream_repo == ""
    assert config.active_agents == []


def test_save_creates_agent_dir_if_missing(tmp_path):
    config = B1Config(upstream_repo="https://github.com/org/repo", active_agents=["CLAUDE"])
    config.save(tmp_path)
    assert (tmp_path / ".agent" / "config.yaml").exists()


def test_save_writes_correct_content(tmp_path):
    config = B1Config(upstream_repo="https://github.com/org/repo", active_agents=["CLAUDE", "GEMINI"])
    config.save(tmp_path)
    data = yaml.safe_load((tmp_path / ".agent" / "config.yaml").read_text(encoding="utf-8"))
    assert data["upstream_repo"] == "https://github.com/org/repo"
    assert data["active_agents"] == ["CLAUDE", "GEMINI"]


def test_save_overwrites_existing_config(tmp_path):
    (tmp_path / ".agent").mkdir()
    (tmp_path / ".agent" / "config.yaml").write_text(
        yaml.dump({"upstream_repo": "old", "active_agents": []}),
        encoding="utf-8",
    )
    B1Config(upstream_repo="new", active_agents=["GEMINI"]).save(tmp_path)
    data = yaml.safe_load((tmp_path / ".agent" / "config.yaml").read_text(encoding="utf-8"))
    assert data["upstream_repo"] == "new"
    assert data["active_agents"] == ["GEMINI"]
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/unit/test_config.py -v
```

Expected: 6 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_config.py
git commit -m "test: add unit tests for B1Config load and save"
```

---

## Task 4: Unit Tests — schema.py

**Files:**
- Create: `tests/unit/test_schema.py`

- [ ] **Step 1: Write tests**

```python
# tests/unit/test_schema.py
import yaml
import pytest
from pathlib import Path
from b1.core.schema import ModuleConfig, ModuleType, SkillConfig


def _write_module_yaml(path: Path, data: dict) -> Path:
    yaml_path = path / "b1-module.yaml"
    yaml_path.write_text(yaml.dump(data), encoding="utf-8")
    return yaml_path


def test_from_yaml_deserializes_minimal_config(tmp_path):
    yaml_path = _write_module_yaml(tmp_path, {
        "name": "my-module",
        "version": "1.0.0",
        "type": "development",
        "skills": [],
        "hooks": {},
    })
    config = ModuleConfig.from_yaml(yaml_path)
    assert config.name == "my-module"
    assert config.version == "1.0.0"
    assert config.type == ModuleType.development


def test_from_yaml_deserializes_skills(tmp_path):
    yaml_path = _write_module_yaml(tmp_path, {
        "name": "my-module",
        "version": "1.0.0",
        "type": "development",
        "skills": [{"name": "my-skill", "install_command": "echo hello"}],
        "hooks": {},
    })
    config = ModuleConfig.from_yaml(yaml_path)
    assert len(config.skills) == 1
    assert config.skills[0].name == "my-skill"
    assert config.skills[0].install_command == "echo hello"


def test_from_yaml_accepts_module_yaml_filename(tmp_path):
    yaml_path = tmp_path / "module.yaml"
    yaml_path.write_text(yaml.dump({
        "name": "alt-module",
        "version": "2.0.0",
        "type": "deployment",
        "skills": [],
        "hooks": {},
    }), encoding="utf-8")
    config = ModuleConfig.from_yaml(yaml_path)
    assert config.name == "alt-module"
    assert config.type == ModuleType.deployment


def test_from_yaml_raises_file_not_found_for_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        ModuleConfig.from_yaml(tmp_path / "nonexistent.yaml")


def test_from_yaml_raises_value_error_for_empty_file(tmp_path):
    yaml_path = tmp_path / "b1-module.yaml"
    yaml_path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError):
        ModuleConfig.from_yaml(yaml_path)


def test_module_type_enum_values():
    assert ModuleType.development == "development"
    assert ModuleType.deployment == "deployment"
    assert ModuleType.cross_cutting == "cross_cutting"
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/unit/test_schema.py -v
```

Expected: 6 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_schema.py
git commit -m "test: add unit tests for ModuleConfig schema"
```

---

## Task 5: Unit Tests — scaffolder.py

**Files:**
- Create: `tests/unit/test_scaffolder.py`

- [ ] **Step 1: Write tests**

```python
# tests/unit/test_scaffolder.py
from pathlib import Path
from b1.core.scaffolder import scaffold_project


def test_creates_agent_directory(tmp_path):
    scaffold_project(tmp_path)
    assert (tmp_path / ".agent").is_dir()


def test_creates_docs_directory(tmp_path):
    scaffold_project(tmp_path)
    assert (tmp_path / "docs").is_dir()


def test_creates_gitignore(tmp_path):
    scaffold_project(tmp_path)
    assert (tmp_path / ".gitignore").exists()


def test_gitignore_contains_python_entries(tmp_path):
    scaffold_project(tmp_path)
    content = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    assert "__pycache__/" in content
    assert ".venv/" in content


def test_creates_readme(tmp_path):
    scaffold_project(tmp_path)
    assert (tmp_path / "README.md").exists()


def test_is_idempotent_does_not_overwrite_existing_gitignore(tmp_path):
    (tmp_path / ".gitignore").write_text("custom content", encoding="utf-8")
    scaffold_project(tmp_path)
    assert (tmp_path / ".gitignore").read_text(encoding="utf-8") == "custom content"


def test_is_idempotent_does_not_overwrite_existing_readme(tmp_path):
    (tmp_path / "README.md").write_text("# My Project", encoding="utf-8")
    scaffold_project(tmp_path)
    assert (tmp_path / "README.md").read_text(encoding="utf-8") == "# My Project"


def test_safe_to_call_twice(tmp_path):
    scaffold_project(tmp_path)
    scaffold_project(tmp_path)  # should not raise
    assert (tmp_path / ".agent").is_dir()
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/unit/test_scaffolder.py -v
```

Expected: 8 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_scaffolder.py
git commit -m "test: add unit tests for scaffold_project"
```

---

## Task 6: Unit Tests — context_manager.py

**Files:**
- Create: `tests/unit/test_context_manager.py`

- [ ] **Step 1: Write tests**

```python
# tests/unit/test_context_manager.py
from pathlib import Path
from b1.core.context_manager import setup_context


def _agent_dir(root: Path) -> Path:
    return root / ".agent" / "project"


def test_creates_root_agent_md_when_missing(tmp_path):
    (tmp_path / ".agent" / "project").mkdir(parents=True)
    setup_context(tmp_path)
    assert (tmp_path / "agent.md").exists()


def test_root_agent_md_contains_b1_marker(tmp_path):
    (tmp_path / ".agent" / "project").mkdir(parents=True)
    setup_context(tmp_path)
    content = (tmp_path / "agent.md").read_text(encoding="utf-8")
    assert "b1CodingTool" in content


def test_appends_to_existing_agent_md_without_marker(tmp_path):
    (tmp_path / ".agent" / "project").mkdir(parents=True)
    (tmp_path / "agent.md").write_text("# Existing content\n", encoding="utf-8")
    setup_context(tmp_path)
    content = (tmp_path / "agent.md").read_text(encoding="utf-8")
    assert "Existing content" in content
    assert "b1CodingTool" in content


def test_does_not_modify_agent_md_with_marker_already_present(tmp_path):
    (tmp_path / ".agent" / "project").mkdir(parents=True)
    original = "# b1CodingTool: Global Context\nAlready configured.\n"
    (tmp_path / "agent.md").write_text(original, encoding="utf-8")
    setup_context(tmp_path)
    assert (tmp_path / "agent.md").read_text(encoding="utf-8") == original


def test_creates_project_agent_md(tmp_path):
    (tmp_path / ".agent" / "project").mkdir(parents=True)
    setup_context(tmp_path)
    assert (tmp_path / ".agent" / "project" / "agent.md").exists()


def test_project_agent_md_contains_project_context_heading(tmp_path):
    (tmp_path / ".agent" / "project").mkdir(parents=True)
    setup_context(tmp_path)
    content = (tmp_path / ".agent" / "project" / "agent.md").read_text(encoding="utf-8")
    assert "Project Context" in content


def test_does_not_overwrite_existing_project_agent_md(tmp_path):
    (tmp_path / ".agent" / "project").mkdir(parents=True)
    proj_md = tmp_path / ".agent" / "project" / "agent.md"
    proj_md.write_text("# Custom project context\n", encoding="utf-8")
    setup_context(tmp_path)
    assert proj_md.read_text(encoding="utf-8") == "# Custom project context\n"
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/unit/test_context_manager.py -v
```

Expected: 7 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_context_manager.py
git commit -m "test: add unit tests for setup_context"
```

---

## Task 7: Unit Tests — compiler.py

**Files:**
- Create: `tests/unit/test_compiler.py`

- [ ] **Step 1: Write tests**

```python
# tests/unit/test_compiler.py
from pathlib import Path
from b1.core.compiler import ContextCompiler


def _scaffold(root: Path, root_md=None, project_md=None, modules=None):
    """Helper: builds a minimal project layout in root."""
    (root / ".agent" / "project").mkdir(parents=True)
    (root / ".agent" / "modules").mkdir(parents=True)
    if root_md is not None:
        (root / "agent.md").write_text(root_md, encoding="utf-8")
    if project_md is not None:
        (root / ".agent" / "project" / "agent.md").write_text(project_md, encoding="utf-8")
    if modules:
        for name, context_files in modules.items():
            mod_ctx = root / ".agent" / "modules" / name / "context"
            mod_ctx.mkdir(parents=True)
            for fname, content in context_files.items():
                (mod_ctx / fname).write_text(content, encoding="utf-8")


def test_compile_returns_empty_string_when_no_files(tmp_path):
    (tmp_path / ".agent" / "modules").mkdir(parents=True)
    compiler = ContextCompiler(tmp_path)
    assert compiler.compile() == ""


def test_compile_includes_root_agent_md(tmp_path):
    _scaffold(tmp_path, root_md="# Root context\n")
    result = ContextCompiler(tmp_path).compile()
    assert "Root context" in result


def test_compile_includes_project_agent_md(tmp_path):
    _scaffold(tmp_path, project_md="# Project context\n")
    result = ContextCompiler(tmp_path).compile()
    assert "Project context" in result


def test_compile_includes_module_context_files(tmp_path):
    _scaffold(tmp_path, modules={"django": {"best-practices.md": "# Django tips\n"}})
    result = ContextCompiler(tmp_path).compile()
    assert "Django tips" in result


def test_compile_includes_all_modules(tmp_path):
    _scaffold(tmp_path, modules={
        "django": {"conventions.md": "Django conventions"},
        "fastapi": {"best-practices.md": "FastAPI tips"},
    })
    result = ContextCompiler(tmp_path).compile()
    assert "Django conventions" in result
    assert "FastAPI tips" in result


def test_compile_includes_html_comment_headers(tmp_path):
    _scaffold(tmp_path, root_md="# Root\n", modules={"django": {"best-practices.md": "# tips"}})
    result = ContextCompiler(tmp_path).compile()
    assert "<!-- b1CodingTool:" in result


def test_compile_handles_missing_modules_dir_gracefully(tmp_path):
    (tmp_path / ".agent" / "project").mkdir(parents=True)
    (tmp_path / "agent.md").write_text("# Root\n", encoding="utf-8")
    # no modules dir at all
    result = ContextCompiler(tmp_path).compile()
    assert "Root" in result
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/unit/test_compiler.py -v
```

Expected: 7 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_compiler.py
git commit -m "test: add unit tests for ContextCompiler"
```

---

## Task 8: Unit Tests — translator.py

**Files:**
- Create: `tests/unit/test_translator.py`

- [ ] **Step 1: Write tests**

```python
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
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/unit/test_translator.py -v
```

Expected: 6 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_translator.py
git commit -m "test: add unit tests for AgentTranslator"
```

---

## Task 9: Unit Tests — fetcher.py

**Files:**
- Create: `tests/unit/test_fetcher.py`

- [ ] **Step 1: Write tests**

```python
# tests/unit/test_fetcher.py
import subprocess
import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
from b1.core.fetcher import ModuleFetcher


def _make_local_module(base: Path, name="test-module") -> Path:
    mod_dir = base / name
    mod_dir.mkdir(parents=True)
    (mod_dir / "b1-module.yaml").write_text(
        yaml.dump({"name": name, "version": "1.0.0", "type": "development", "skills": [], "hooks": {}}),
        encoding="utf-8",
    )
    return mod_dir


def _fetcher(tmp_path) -> ModuleFetcher:
    """Create a ModuleFetcher with cache_dir redirected to tmp_path."""
    fetcher = ModuleFetcher()
    fetcher.cache_dir = tmp_path / "cache"
    fetcher.cache_dir.mkdir(parents=True, exist_ok=True)
    return fetcher


def test_fetch_local_path_returns_module_dir(tmp_path):
    mod_dir = _make_local_module(tmp_path)
    fetcher = _fetcher(tmp_path)
    result = fetcher.fetch(str(mod_dir))
    assert result == mod_dir


def test_fetch_local_path_missing_raises_value_error(tmp_path):
    fetcher = _fetcher(tmp_path)
    with pytest.raises(ValueError, match="Invalid module source"):
        fetcher.fetch(str(tmp_path / "nonexistent"))


def test_fetch_local_path_without_yaml_raises_value_error(tmp_path):
    bare_dir = tmp_path / "bare"
    bare_dir.mkdir()
    fetcher = _fetcher(tmp_path)
    with pytest.raises(ValueError, match="Invalid module source"):
        fetcher.fetch(str(bare_dir))


def test_fetch_git_url_clones_on_first_fetch(tmp_path):
    fetcher = _fetcher(tmp_path)
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        # Simulate a successful clone by creating the target dir
        target = fetcher.cache_dir / "my-module"
        target.mkdir()
        _make_local_module(target, "my-module")

        fetcher.fetch("https://github.com/org/my-module.git")

    # git clone should have been the first subprocess call
    first_call_args = mock_run.call_args_list[0][0][0]
    assert first_call_args[0] == "git"
    assert first_call_args[1] == "clone"


def test_fetch_git_url_pulls_when_cache_exists(tmp_path):
    fetcher = _fetcher(tmp_path)
    # Pre-create the cache entry to simulate an existing clone
    cached = fetcher.cache_dir / "my-module"
    _make_local_module(cached, "my-module")

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        fetcher.fetch("https://github.com/org/my-module.git")

    first_call_args = mock_run.call_args_list[0][0][0]
    assert first_call_args[0] == "git"
    assert first_call_args[1] == "-C"
    assert first_call_args[3] == "pull"


def test_fetch_git_url_raises_on_clone_failure(tmp_path):
    fetcher = _fetcher(tmp_path)
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "git", stderr=b"auth failed")
        with pytest.raises(subprocess.CalledProcessError):
            fetcher.fetch("https://github.com/org/my-module.git")
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/unit/test_fetcher.py -v
```

Expected: 6 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_fetcher.py
git commit -m "test: add unit tests for ModuleFetcher"
```

---

## Task 10: Unit Tests — installer.py

**Files:**
- Create: `tests/unit/test_installer.py`

- [ ] **Step 1: Write tests**

```python
# tests/unit/test_installer.py
import subprocess
import yaml
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from b1.core.installer import ModuleInstaller


def _make_module_source(base: Path, name="test-module", skills=None) -> Path:
    mod_dir = base / name
    mod_dir.mkdir(parents=True)
    config = {
        "name": name,
        "version": "1.0.0",
        "type": "development",
        "description": "A test module",
        "skills": skills or [],
        "hooks": {},
    }
    (mod_dir / "b1-module.yaml").write_text(yaml.dump(config), encoding="utf-8")
    (mod_dir / "context").mkdir()
    (mod_dir / "context" / "best-practices.md").write_text("# Best practices\n", encoding="utf-8")
    return mod_dir


def _project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    (project / ".agent" / "modules").mkdir(parents=True)
    return project


def test_install_copies_files_to_modules_dir(tmp_path):
    src = _make_module_source(tmp_path / "src")
    project = _project(tmp_path)
    ModuleInstaller(project).install(src)
    assert (project / ".agent" / "modules" / "test-module").is_dir()


def test_install_preserves_context_files(tmp_path):
    src = _make_module_source(tmp_path / "src")
    project = _project(tmp_path)
    ModuleInstaller(project).install(src)
    assert (project / ".agent" / "modules" / "test-module" / "context" / "best-practices.md").exists()


def test_install_overwrites_existing_module(tmp_path):
    src = _make_module_source(tmp_path / "src")
    project = _project(tmp_path)
    installer = ModuleInstaller(project)
    installer.install(src)
    # Modify source and install again
    (src / "context" / "new-file.md").write_text("New file\n", encoding="utf-8")
    installer.install(src)
    assert (project / ".agent" / "modules" / "test-module" / "context" / "new-file.md").exists()


def test_install_raises_when_no_yaml_found(tmp_path):
    bare = tmp_path / "bare"
    bare.mkdir()
    project = _project(tmp_path)
    with pytest.raises(FileNotFoundError):
        ModuleInstaller(project).install(bare)


def test_install_runs_skill_command(tmp_path):
    src = _make_module_source(
        tmp_path / "src",
        skills=[{"name": "my-skill", "install_command": "echo hello"}],
    )
    project = _project(tmp_path)
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        ModuleInstaller(project).install(src)
    mock_run.assert_called_once()
    call_kwargs = mock_run.call_args[1]
    assert call_kwargs.get("shell") is True


def test_install_continues_when_skill_command_fails(tmp_path):
    src = _make_module_source(
        tmp_path / "src",
        skills=[{"name": "bad-skill", "install_command": "exit 1"}],
    )
    project = _project(tmp_path)
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "exit 1", stderr="error")
        # Should NOT raise — installation continues despite skill failure
        ModuleInstaller(project).install(src)
    assert (project / ".agent" / "modules" / "test-module").is_dir()
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/unit/test_installer.py -v
```

Expected: 6 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/unit/test_installer.py
git commit -m "test: add unit tests for ModuleInstaller"
```

---

## Task 11: Integration Tests — init command

**Files:**
- Create: `tests/integration/test_init_cmd.py`

- [ ] **Step 1: Write tests**

```python
# tests/integration/test_init_cmd.py
from pathlib import Path
from typer.testing import CliRunner
from b1.cli import app

runner = CliRunner()


def test_init_creates_agent_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert (tmp_path / ".agent").is_dir()


def test_init_creates_docs_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    assert (tmp_path / "docs").is_dir()


def test_init_creates_agent_md(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    assert (tmp_path / "agent.md").exists()


def test_init_creates_project_agent_md(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    assert (tmp_path / ".agent" / "project" / "agent.md").exists()


def test_init_creates_gitignore(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    assert (tmp_path / ".gitignore").exists()


def test_init_creates_readme(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init"])
    assert (tmp_path / "README.md").exists()


def test_init_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".gitignore").write_text("custom", encoding="utf-8")
    runner.invoke(app, ["init"])
    runner.invoke(app, ["init"])
    assert (tmp_path / ".gitignore").read_text(encoding="utf-8") == "custom"


def test_init_with_path_argument_creates_subdirectory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "my-project"
    result = runner.invoke(app, ["init", str(target)])
    assert result.exit_code == 0
    assert (target / ".agent").is_dir()


def test_init_creates_directory_if_it_does_not_exist(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    new_dir = tmp_path / "brand-new"
    result = runner.invoke(app, ["init", str(new_dir)])
    assert result.exit_code == 0
    assert new_dir.is_dir()
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/integration/test_init_cmd.py -v
```

Expected: 9 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_init_cmd.py
git commit -m "test: add integration tests for b1 init command"
```

---

## Task 12: Integration Tests — install command

**Files:**
- Create: `tests/integration/test_install_cmd.py`

- [ ] **Step 1: Write tests**

```python
# tests/integration/test_install_cmd.py
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from b1.cli import app

runner = CliRunner()


def _make_module_source(base: Path, name="django") -> Path:
    mod_dir = base / name
    (mod_dir / "context").mkdir(parents=True)
    (mod_dir / "b1-module.yaml").write_text(yaml.dump({
        "name": name, "version": "1.0.0", "type": "development",
        "description": "Test", "skills": [], "hooks": {},
    }), encoding="utf-8")
    (mod_dir / "context" / "best-practices.md").write_text("# Tips\n", encoding="utf-8")
    return mod_dir


def test_install_copies_module_to_agent_modules(tmp_path, monkeypatch, make_project):
    project = make_project()
    monkeypatch.chdir(project)
    src = _make_module_source(tmp_path / "src")

    with patch("b1.commands.install.ModuleFetcher") as MockFetcher:
        MockFetcher.return_value.fetch.return_value = src
        result = runner.invoke(app, ["install", str(src)])

    assert result.exit_code == 0
    assert (project / ".agent" / "modules" / "django").is_dir()


def test_install_preserves_context_files(tmp_path, monkeypatch, make_project):
    project = make_project()
    monkeypatch.chdir(project)
    src = _make_module_source(tmp_path / "src")

    with patch("b1.commands.install.ModuleFetcher") as MockFetcher:
        MockFetcher.return_value.fetch.return_value = src
        runner.invoke(app, ["install", str(src)])

    assert (project / ".agent" / "modules" / "django" / "context" / "best-practices.md").exists()


def test_install_exits_with_error_outside_initialized_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["install", "/some/path"])
    assert result.exit_code != 0


def test_install_exits_with_error_for_invalid_source(tmp_path, monkeypatch, make_project):
    project = make_project()
    monkeypatch.chdir(project)

    with patch("b1.commands.install.ModuleFetcher") as MockFetcher:
        MockFetcher.return_value.fetch.side_effect = ValueError("not found")
        result = runner.invoke(app, ["install", "/nonexistent/path"])

    assert result.exit_code != 0
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/integration/test_install_cmd.py -v
```

Expected: 4 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_install_cmd.py
git commit -m "test: add integration tests for b1 install command"
```

---

## Task 13: Integration Tests — pair command

**Files:**
- Create: `tests/integration/test_pair_cmd.py`

- [ ] **Step 1: Write tests**

```python
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
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/integration/test_pair_cmd.py -v
```

Expected: 6 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_pair_cmd.py
git commit -m "test: add integration tests for b1 pair command"
```

---

## Task 14: Integration Tests — pull command

**Files:**
- Create: `tests/integration/test_pull_cmd.py`

- [ ] **Step 1: Write tests**

```python
# tests/integration/test_pull_cmd.py
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from b1.cli import app

runner = CliRunner()


def test_pull_exits_zero_with_no_modules_installed(make_project, monkeypatch):
    project = make_project()
    monkeypatch.chdir(project)
    result = runner.invoke(app, ["pull"])
    assert result.exit_code == 0


def test_pull_exits_zero_when_modules_dir_missing(tmp_path, monkeypatch):
    # Initialized project but no modules dir at all
    (tmp_path / ".agent").mkdir()
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["pull"])
    assert result.exit_code == 0


def test_pull_skips_module_not_in_cache(make_project, monkeypatch):
    project = make_project(modules=["django"])
    monkeypatch.chdir(project)

    with patch("b1.commands.pull.ModuleFetcher") as MockFetcher:
        instance = MockFetcher.return_value
        instance.cache_dir = project / "fake_cache"  # empty dir — django not present
        instance.cache_dir.mkdir()
        result = runner.invoke(app, ["pull"])

    assert result.exit_code == 0
    assert "Skipping" in result.output or "not found" in result.output.lower()


def test_pull_fetches_and_reinstalls_each_cached_module(make_project, make_module, monkeypatch):
    project = make_project(modules=["django"])
    monkeypatch.chdir(project)
    django_src = make_module(name="django")

    with patch("b1.commands.pull.ModuleFetcher") as MockFetcher:
        instance = MockFetcher.return_value
        fake_cache = project / "fake_cache"
        fake_cache.mkdir()
        (fake_cache / "django").mkdir()  # simulate django in cache
        instance.cache_dir = fake_cache
        instance.fetch.return_value = django_src

        with patch("b1.commands.pull.ModuleInstaller") as MockInstaller:
            result = runner.invoke(app, ["pull"])
            MockInstaller.return_value.install.assert_called_once_with(django_src)

    assert result.exit_code == 0
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/integration/test_pull_cmd.py -v
```

Expected: 4 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_pull_cmd.py
git commit -m "test: add integration tests for b1 pull command"
```

---

## Task 15: Integration Tests — push command

**Files:**
- Create: `tests/integration/test_push_cmd.py`

- [ ] **Step 1: Write tests**

```python
# tests/integration/test_push_cmd.py
import subprocess
from unittest.mock import patch, MagicMock, call
from typer.testing import CliRunner
from b1.cli import app

runner = CliRunner()

# All subprocess calls are mocked — no real git or gh required.
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
            mock_run.return_value = _successful_run(stdout="https://github.com/org/repo/pull/1")
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
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/integration/test_push_cmd.py -v
```

Expected: 4 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_push_cmd.py
git commit -m "test: add integration tests for b1 push command"
```

---

## Task 16: Integration Tests — FastAPI server

**Files:**
- Create: `tests/integration/test_server.py`

- [ ] **Step 1: Write tests**

```python
# tests/integration/test_server.py
import pytest
from fastapi.testclient import TestClient
from b1.server.main import app


# TestClient from fastapi/starlette runs the ASGI app in-process — no real server.
# Path.cwd() is set by cd_project/monkeypatch.chdir before each test.

@pytest.fixture
def client(cd_project):
    with TestClient(app) as c:
        yield c


def test_get_project_returns_name_and_initialized_true(client, cd_project):
    resp = client.get("/api/project")
    assert resp.status_code == 200
    data = resp.json()
    assert data["initialized"] is True
    assert data["name"] == cd_project.name


def test_get_config_returns_config_shape(client):
    resp = client.get("/api/config")
    assert resp.status_code == 200
    data = resp.json()
    assert "upstream_repo" in data
    assert "active_agents" in data


def test_get_modules_returns_empty_list_with_no_modules(client):
    resp = client.get("/api/modules")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_modules_returns_installed_modules(make_project, monkeypatch):
    project = make_project(modules=["django"])
    monkeypatch.chdir(project)
    with TestClient(app) as client:
        resp = client.get("/api/modules")
    assert resp.status_code == 200
    names = [m["name"] for m in resp.json()]
    assert "django" in names


def test_get_context_returns_compiled_content(client):
    resp = client.get("/api/context")
    assert resp.status_code == 200
    data = resp.json()
    assert "content" in data
    assert isinstance(data["content"], str)


def test_get_context_returns_400_when_not_initialized(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with TestClient(app) as client:
        resp = client.get("/api/context")
    assert resp.status_code == 400
```

- [ ] **Step 2: Run tests**

```bash
uv run pytest tests/integration/test_server.py -v
```

Expected: 6 passed.

- [ ] **Step 3: Commit**

```bash
git add tests/integration/test_server.py
git commit -m "test: add integration tests for FastAPI dashboard server"
```

---

## Task 17: Slow / Real-Git Tests

**Files:**
- Create: `tests/slow/test_fetcher_real_git.py`
- Create: `tests/slow/test_push_real_git.py`

- [ ] **Step 1: Write test_fetcher_real_git.py**

```python
# tests/slow/test_fetcher_real_git.py
"""
Tests that make real git calls. Run with: pytest -m slow
Requires git to be installed and on PATH.
"""
import subprocess
import yaml
import pytest
from pathlib import Path
from b1.core.fetcher import ModuleFetcher


@pytest.mark.slow
def test_fetcher_clones_git_repo(tmp_path):
    # Create a bare repo with a valid module structure
    bare_repo = tmp_path / "bare.git"
    work_tree = tmp_path / "work"
    work_tree.mkdir()

    subprocess.run(["git", "init", "--bare", str(bare_repo)], check=True, capture_output=True)
    subprocess.run(["git", "init", str(work_tree)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "config", "user.email", "test@test.com"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "config", "user.name", "Test"], check=True, capture_output=True)

    # Write a valid module into the work tree
    (work_tree / "b1-module.yaml").write_text(yaml.dump({
        "name": "real-module", "version": "1.0.0", "type": "development",
        "skills": [], "hooks": {},
    }), encoding="utf-8")
    subprocess.run(["git", "-C", str(work_tree), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "commit", "-m", "init"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "remote", "add", "origin", str(bare_repo)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "push", "-u", "origin", "HEAD"], check=True, capture_output=True)

    # Now test the fetcher against the bare repo
    fetcher = ModuleFetcher()
    fetcher.cache_dir = tmp_path / "cache"
    fetcher.cache_dir.mkdir()

    result = fetcher.fetch(f"file://{bare_repo}")
    assert result.exists()
    assert (result / "b1-module.yaml").exists()


@pytest.mark.slow
def test_fetcher_pulls_on_second_fetch(tmp_path):
    bare_repo = tmp_path / "bare.git"
    work_tree = tmp_path / "work"
    work_tree.mkdir()

    subprocess.run(["git", "init", "--bare", str(bare_repo)], check=True, capture_output=True)
    subprocess.run(["git", "init", str(work_tree)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "config", "user.email", "test@test.com"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "config", "user.name", "Test"], check=True, capture_output=True)

    (work_tree / "b1-module.yaml").write_text(yaml.dump({
        "name": "bare", "version": "1.0.0", "type": "development",
        "skills": [], "hooks": {},
    }), encoding="utf-8")
    subprocess.run(["git", "-C", str(work_tree), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "commit", "-m", "init"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "remote", "add", "origin", str(bare_repo)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(work_tree), "push", "-u", "origin", "HEAD"], check=True, capture_output=True)

    fetcher = ModuleFetcher()
    fetcher.cache_dir = tmp_path / "cache"
    fetcher.cache_dir.mkdir()

    url = f"file://{bare_repo}"
    fetcher.fetch(url)       # first: clone
    result = fetcher.fetch(url)  # second: pull (should not raise)
    assert result.exists()
```

- [ ] **Step 2: Write test_push_real_git.py**

```python
# tests/slow/test_push_real_git.py
"""
Tests that make real git calls against a local repo. Run with: pytest -m slow
`gh pr create` is still mocked.
"""
import subprocess
import yaml
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from b1.cli import app

runner = CliRunner()


def _init_git_repo(path: Path):
    subprocess.run(["git", "init", str(path)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "test@test.com"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Test"], check=True, capture_output=True)
    # Initial commit so branch operations work
    (path / "README.md").write_text("init\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(path), "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(path), "commit", "-m", "init"], check=True, capture_output=True)


@pytest.mark.slow
def test_push_creates_branch_and_stages_agent_dir(tmp_path, monkeypatch, make_project):
    project = make_project(upstream_repo="org/repo")
    _init_git_repo(project)
    monkeypatch.chdir(project)

    def selective_run(cmd, *args, **kwargs):
        """Pass all git calls through to real subprocess; mock only gh."""
        if isinstance(cmd, list) and cmd[0] == "gh":
            m = MagicMock()
            m.stdout = "https://github.com/org/repo/pull/1"
            m.returncode = 0
            return m
        return subprocess.run(cmd, *args, **kwargs)

    with patch("b1.commands.push.shutil.which", return_value="/usr/bin/gh"):
        with patch("b1.commands.push.subprocess.run", side_effect=selective_run):
            result = runner.invoke(app, ["push"])

    # Verify a b1-learnings-* branch exists
    branches = subprocess.run(
        ["git", "-C", str(project), "branch"],
        capture_output=True, text=True
    ).stdout
    assert "b1-learnings-" in branches
```

- [ ] **Step 3: Run slow tests**

```bash
uv run pytest -m slow -v
```

Expected: 3 passed (or investigation of any git-environment-specific failures).

- [ ] **Step 4: Run the full fast suite to confirm nothing is broken**

```bash
uv run pytest -v
```

Expected: all non-slow tests pass.

- [ ] **Step 5: Commit**

```bash
git add tests/slow/test_fetcher_real_git.py tests/slow/test_push_real_git.py
git commit -m "test: add slow real-git tests for fetcher and push command"
```

---

## Final Verification

- [ ] **Run full suite with coverage**

```bash
uv run pytest --cov=src --cov-report=term-missing
```

Expected: all fast tests pass, coverage report printed. Aim for >80% on core modules.

- [ ] **Final commit if pyproject.toml was modified during implementation**

```bash
git add pyproject.toml
git commit -m "chore: finalize test suite configuration"
```
