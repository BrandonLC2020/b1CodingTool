import pytest
from b1.core.compiler import ContextCompiler
from pathlib import Path

def test_docker_context_compilation(tmp_path):
    # Setup a mock project structure
    modules_dir = tmp_path / ".agents" / "modules" / "docker" / "context"
    modules_dir.mkdir(parents=True)
    (modules_dir / "best-practices.md").write_text("# Docker: Best Practices\n- Use Compose", encoding="utf-8")
    
    # Compile context
    compiler = ContextCompiler(tmp_path)
    result = compiler.compile()
    
    # Verify the context was included
    assert "Docker: Best Practices" in result
    assert "<!-- b1CodingTool: Module Context [docker] - best-practices.md -->" in result
