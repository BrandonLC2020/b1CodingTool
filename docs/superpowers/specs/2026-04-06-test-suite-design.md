# Test Suite Design

**Date:** 2026-04-06
**Scope:** Full test suite for b1CodingTool — unit, integration, and slow/real-git tests

---

## Goal

Eliminate the manual effort of constructing fake project directories for testing. Every test that
needs a project structure, a module source, or a specific filesystem state gets it automatically
via shared pytest fixtures. No test should create directories or files inline.

---

## Framework & Dependencies

**pytest** is the test runner. Two additions to `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "httpx>=0.27",        # FastAPI TestClient
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--tb=short"
markers = [
    "slow: tests that make real git/network calls (run with: pytest -m slow)",
]
```

`httpx` provides the synchronous `TestClient` for FastAPI server tests.
`unittest.mock` (stdlib) handles all subprocess mocking — no `pytest-mock` needed.

**Run commands:**
```bash
uv run pytest               # fast tests (unit + integration)
uv run pytest -m slow       # real-git tests only
uv run pytest --cov=src     # with coverage report
```

---

## Fixture Design (`tests/conftest.py`)

All fixtures are defined in `tests/conftest.py` and available project-wide.

### `make_module(tmp_path)`

Factory fixture. Returns a callable that creates a valid module source directory.

```python
# Usage
def test_install(make_module, ...):
    module_dir = make_module()
    module_dir = make_module(name="django", version="2.0.0")
    module_dir = make_module(
        name="fastapi",
        context_files={"best-practices.md": "# content", "conventions.md": "# more"}
    )
```

Produces:
```
tmp_path/modules/<name>/
  b1-module.yaml
  context/
    <context_files>
```

### `make_project(tmp_path)`

Factory fixture. Returns a callable that creates a fully scaffolded project directory.

```python
# Usage
def test_pair(make_project, ...):
    project = make_project()
    project = make_project(modules=["django", "fastapi"])
    project = make_project(
        agents=["CLAUDE", "GEMINI"],
        upstream_repo="https://github.com/org/repo",
        modules=["django"],
    )
```

Produces:
```
tmp_path/project/
  agent.md
  .agent/
    config.yaml
    project/
      agent.md
    modules/
      <name>/           # one per entry in modules=[]
        b1-module.yaml
        context/
```

When `modules` is provided, `make_project` calls `make_module` internally and copies the result into `.agent/modules/`.

### `cd_project(make_project, monkeypatch)`

Convenience fixture. Creates a default project and `chdir`s into it. Solves the `Path.cwd()` problem — all CLI commands locate the project root via `Path.cwd()`, so tests must run from inside the temp directory.

```python
# Usage — no setup needed, cwd is already the project dir
def test_init_idempotent(cd_project):
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
```

`monkeypatch.chdir()` automatically restores the original working directory after each test.

---

## Unit Tests (`tests/unit/`)

One file per core module. Filesystem operations use `tmp_path` directly. Subprocess calls are
patched with `unittest.mock.patch`. No CLI runner — these call module functions directly.

### `test_config.py`
- `B1Config.load()` returns empty config when `.agent/config.yaml` is missing
- `B1Config.load()` deserializes correctly from valid YAML
- `B1Config.load()` raises on malformed YAML
- `B1Config.save()` creates `.agent/` directory if missing
- `B1Config.save()` writes correct YAML content
- `B1Config.save()` overwrites existing config

### `test_schema.py`
- `ModuleConfig.from_yaml()` deserializes a valid `b1-module.yaml`
- `ModuleConfig.from_yaml()` raises `FileNotFoundError` for missing file
- `ModuleConfig.from_yaml()` raises `ValueError` for empty file
- `ModuleConfig.from_yaml()` accepts both `b1-module.yaml` and `module.yaml` filenames
- `ModuleType` enum has expected values

### `test_scaffolder.py`
- `scaffold_project()` creates `.agent/`, `docs/`, `.gitignore`, `README.md`
- `scaffold_project()` is idempotent — safe to call twice, no files overwritten
- `.gitignore` contains expected Python and b1CodingTool entries
- `README.md` contains expected template content

### `test_context_manager.py`
- `setup_context()` creates root `agent.md` when missing
- `setup_context()` appends b1 marker block when `agent.md` exists but lacks it
- `setup_context()` leaves `agent.md` unchanged when marker already present
- `setup_context()` creates `.agent/project/agent.md` with expected template

### `test_compiler.py`
- `compile()` with no modules returns root + project context only
- `compile()` with one module includes its context files with correct HTML comment headers
- `compile()` with multiple modules includes all in order
- `compile()` handles missing optional files gracefully (no crash)
- HTML comment markers correctly identify each section's origin

### `test_translator.py`
- `generate_files(["CLAUDE", "GEMINI"], content)` writes `CLAUDE.md` and `GEMINI.md`
- Each file includes the auto-generation warning header
- File content matches compiled input content
- Overwrites existing files without error

### `test_fetcher.py`
- Local path: valid module directory returns the path
- Local path: missing directory raises appropriate error
- Local path: directory without YAML raises appropriate error
- Git URL (mocked `subprocess.run`): `git clone` called on first fetch
- Git URL (mocked): `git pull` called when cache directory already exists
- Git URL (mocked): `~/.b1/cache/` created if missing
- `subprocess.CalledProcessError` propagates with helpful message

### `test_installer.py`
- Module files copied to `.agent/modules/<name>/`
- Existing module directory overwritten cleanly
- Skill `install_command` executed via subprocess
- Skill command failure is logged but does not abort installation
- Both `b1-module.yaml` and `module.yaml` filenames recognized

---

## Integration Tests (`tests/integration/`)

Use Typer's `CliRunner` (via Click) to invoke CLI commands end-to-end against real temp directories.
Only `subprocess.run` is mocked (for git/gh calls). All filesystem operations are real.

```python
from typer.testing import CliRunner
from b1.cli import app

runner = CliRunner()
```

### `test_init_cmd.py`
- Fresh empty directory: all expected files and dirs created
- Running `init` twice: idempotent, no files overwritten
- `init <path>`: creates and initializes a named subdirectory
- Exit code 0 on success

### `test_install_cmd.py`
- Valid local module path: installed to `.agent/modules/<name>/`
- Running outside initialized project (no `.agent/`): exits with non-zero code and error message
- Invalid/missing source path: exits with non-zero code
- Module context files preserved after install

### `test_pair_cmd.py`
- `CLAUDE.md`, `GEMINI.md`, `CODEX.md` written to project root
- Content includes root `agent.md`, project `agent.md`, and installed module context
- Running outside initialized project exits with error
- Re-running after adding a module updates the output files

### `test_pull_cmd.py`
- Each installed module triggers a fetch (mocked subprocess)
- Empty `.agent/modules/` directory does not crash
- Missing module in cache handled gracefully with warning

### `test_push_cmd.py`
All git and `gh` subprocess calls are mocked.
- Git branch created with `b1-learnings-{timestamp}` pattern
- `.agent/` directory staged for commit
- `gh pr create` called with `--draft` flag
- Exits cleanly if no changes to stage
- Prompts for upstream repo if not in config; saves to config after entry

### `test_server.py`
Uses `httpx.TestClient` — no real Uvicorn server started.
- `GET /api/project` returns project name, path, and `initialized: true`
- `GET /api/config` returns config shape with `upstream_repo` and `active_agents`
- `GET /api/modules` returns list of installed modules with metadata
- `GET /api/context` returns compiled markdown content
- `GET /api/context` on uninitialized project returns HTTP 400

---

## Slow / Real-Git Tests (`tests/slow/`)

Marked `@pytest.mark.slow`. Skipped in normal `pytest` runs. Use actual git commands against
temp bare repositories — no mocking.

### `test_fetcher_real_git.py`
1. `git init --bare` a temp repo; add a valid module directory and commit
2. Call `fetcher.fetch(git_url)` pointing at the bare repo
3. Assert module files cloned to cache dir — `ModuleFetcher` instantiated with `cache_dir=tmp_path` to avoid writing to real `~/.b1/cache/`
4. Call `fetch()` again — assert `git pull` invoked (not `git clone`)

### `test_push_real_git.py`
1. `git init` a project in `tmp_path`; make an initial commit
2. Run `push_cmd()` in that directory
3. Assert new branch `b1-learnings-*` created
4. Assert `.agent/` files staged
5. `gh pr create` still mocked — not testing GitHub CLI integration

---

## Directory Layout

```
tests/
├── conftest.py                       # make_module, make_project, cd_project
├── unit/
│   ├── test_config.py
│   ├── test_schema.py
│   ├── test_scaffolder.py
│   ├── test_context_manager.py
│   ├── test_compiler.py
│   ├── test_translator.py
│   ├── test_fetcher.py
│   └── test_installer.py
├── integration/
│   ├── test_init_cmd.py
│   ├── test_install_cmd.py
│   ├── test_pair_cmd.py
│   ├── test_pull_cmd.py
│   ├── test_push_cmd.py
│   └── test_server.py
└── slow/
    ├── test_fetcher_real_git.py
    └── test_push_real_git.py
```

---

## What This Eliminates

Before: manually create `.agent/`, `b1-module.yaml`, `agent.md`, `config.yaml`, context files,
and `chdir` — for every test.

After:
```python
def test_pair_includes_module_context(cd_project, make_module):
    module = make_module(name="django", context_files={"best-practices.md": "# Django tips"})
    runner.invoke(app, ["install", str(module)])
    result = runner.invoke(app, ["pair"])
    assert "Django tips" in Path("CLAUDE.md").read_text()
```

Three lines of test body. All setup is fixture-driven.
