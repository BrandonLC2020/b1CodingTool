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
