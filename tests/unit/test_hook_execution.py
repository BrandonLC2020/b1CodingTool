import subprocess
import yaml
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from b1.core.installer import ModuleInstaller

def _make_module_source_with_hook(base: Path, name="test-module", hooks=None) -> Path:
    mod_dir = base / name
    mod_dir.mkdir(parents=True)
    config = {
        "name": name,
        "version": "1.0.0",
        "type": "development",
        "description": "A test module",
        "skills": [],
        "hooks": hooks or {},
    }
    (mod_dir / "b1-module.yaml").write_text(yaml.dump(config), encoding="utf-8")
    # Create the hook script
    for hook_command in hooks.values():
        (mod_dir / hook_command).write_text("#!/bin/bash\necho test", encoding="utf-8")
    
    (mod_dir / "context").mkdir()
    (mod_dir / "context" / "best-practices.md").write_text("# Best practices\n", encoding="utf-8")
    return mod_dir

def _project(tmp_path: Path) -> Path:
    project = tmp_path / "project"
    (project / ".agent" / "modules").mkdir(parents=True)
    return project

def test_install_runs_post_install_hook(tmp_path):
    hook_command = "post-install.sh"
    src = _make_module_source_with_hook(
        tmp_path / "src",
        hooks={"post-install": hook_command},
    )
    project = _project(tmp_path)
    
    with patch("b1.core.hook_engine.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        ModuleInstaller(project).install(src)
    
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    # Check that it uses a list and shell=False
    assert isinstance(args[0], list)
    assert kwargs.get("shell") is False
    assert kwargs.get("cwd") == project
    # The script path should point to the installed module directory
    assert "post-install.sh" in args[0][0]

def test_install_hook_failure_shows_stdout_and_stderr(tmp_path):
    hook_command = "fail.sh"
    src = _make_module_source_with_hook(
        tmp_path / "src",
        hooks={"post-install": hook_command},
    )
    project = _project(tmp_path)
    
    with patch("b1.core.hook_engine.subprocess.run") as mock_run, \
         patch("b1.core.hook_engine.console.print") as mock_print:
        
        e = subprocess.CalledProcessError(1, "fail.sh")
        e.stdout = "some output"
        e.stderr = "some error"
        mock_run.side_effect = e
        
        ModuleInstaller(project).install(src)
        
    # Verify console.print was called with stdout and stderr
    print_calls = [str(call) for call in mock_print.call_args_list]
    assert any("some output" in call for call in print_calls)
    assert any("some error" in call for call in print_calls)
