import subprocess
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import yaml

from b1.core.hook_engine import HookEngine

def _make_module_with_hook(modules_dir: Path, name: str, hook_name: str, hook_cmd: str):
    mod_dir = modules_dir / name
    mod_dir.mkdir(parents=True)
    config = {
        "name": name,
        "version": "1.0.0",
        "type": "development",
        "hooks": {hook_name: hook_cmd}
    }
    (mod_dir / "b1-module.yaml").write_text(yaml.dump(config), encoding="utf-8")
    
    script_path = mod_dir / hook_cmd
    script_path.write_text("#!/bin/bash\necho test", encoding="utf-8")
    script_path.chmod(0o755)
    return mod_dir

def test_hook_engine_runs_scripts(tmp_path):
    project = tmp_path / "project"
    modules_dir = project / ".agent" / "modules"
    modules_dir.mkdir(parents=True)
    
    _make_module_with_hook(modules_dir, "test-mod", "pre-pair", "pre-pair.sh")
    
    engine = HookEngine(project)
    
    with patch("b1.core.hook_engine.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        engine.run_hooks("pre-pair")
        
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert "pre-pair.sh" in args[0][0]
    assert kwargs["cwd"] == project

def test_hook_engine_runs_shell_fallback(tmp_path):
    project = tmp_path / "project"
    modules_dir = project / ".agent" / "modules"
    modules_dir.mkdir(parents=True)
    
    # Hook command that is NOT a file
    mod_dir = modules_dir / "test-mod"
    mod_dir.mkdir(parents=True)
    config = {
        "name": "test-mod",
        "version": "1.0.0",
        "type": "development",
        "hooks": {"post-install": "echo 'hello'"}
    }
    (mod_dir / "b1-module.yaml").write_text(yaml.dump(config), encoding="utf-8")
    
    engine = HookEngine(project)
    
    with patch("b1.core.hook_engine.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        engine.run_hooks("post-install")
        
    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    assert args[0] == "echo 'hello'"
    assert kwargs["shell"] is True

def test_hook_engine_skips_missing_hook(tmp_path):
    project = tmp_path / "project"
    modules_dir = project / ".agent" / "modules"
    modules_dir.mkdir(parents=True)
    
    _make_module_with_hook(modules_dir, "test-mod", "pre-pair", "pre-pair.sh")
    
    engine = HookEngine(project)
    
    with patch("b1.core.hook_engine.subprocess.run") as mock_run:
        engine.run_hooks("post-pair")
        
    mock_run.assert_not_called()
