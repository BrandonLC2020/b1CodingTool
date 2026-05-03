import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
from b1.core.fetcher import ModuleFetcher
from b1.core.schema import ModuleConfig
from b1.core.exceptions import NetworkError, ValidationError

def test_fetcher_timeout(tmp_path):
    fetcher = ModuleFetcher(timeout=0.1)
    fetcher.cache_dir = tmp_path / "cache"
    fetcher.cache_dir.mkdir()
    
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(["git", "clone"], 0.1)
        with pytest.raises(NetworkError) as excinfo:
            fetcher.fetch("https://github.com/org/repo.git")
        assert "timed out" in excinfo.value.message
        assert any("timeout" in s.lower() for s in excinfo.value.suggestions)

def test_fetcher_ssl_error(tmp_path):
    fetcher = ModuleFetcher()
    fetcher.cache_dir = tmp_path / "cache"
    fetcher.cache_dir.mkdir()
    
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, "git", stderr=b"SSL certificate problem")
        with pytest.raises(NetworkError) as excinfo:
            fetcher.fetch("https://github.com/org/repo.git")
        assert "Failed to clone" in excinfo.value.message
        assert any("SSL" in s for s in excinfo.value.suggestions)

def test_config_invalid_name(tmp_path):
    config_file = tmp_path / "b1-module.yaml"
    config_file.write_text("name: 'invalid name!'\nversion: 1.0.0\ntype: development", encoding="utf-8")
    
    with pytest.raises(ValidationError) as excinfo:
        ModuleConfig.from_yaml(config_file)
    assert "Module name" in str(excinfo.value)

def test_config_invalid_version(tmp_path):
    config_file = tmp_path / "b1-module.yaml"
    config_file.write_text("name: valid-name\nversion: '1.0'\ntype: development", encoding="utf-8")
    
    with pytest.raises(ValidationError) as excinfo:
        ModuleConfig.from_yaml(config_file)
    assert "Version" in str(excinfo.value)

def test_config_missing_required_field(tmp_path):
    config_file = tmp_path / "b1-module.yaml"
    config_file.write_text("name: valid-name\nversion: 1.0.0", encoding="utf-8") # type is missing
    
    with pytest.raises(ValidationError) as excinfo:
        ModuleConfig.from_yaml(config_file)
    assert "type" in str(excinfo.value)
