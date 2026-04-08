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
