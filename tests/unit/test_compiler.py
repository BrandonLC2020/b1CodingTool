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
