"""Tests that the three new GitHub tool-base manifests parse correctly via ModuleConfig."""
from pathlib import Path

import pytest

from b1.core.schema import ModuleConfig, ModuleType

MODULES_ROOT = Path(__file__).resolve().parents[2] / "modules" / "deployment"


def _load(module_name: str) -> ModuleConfig:
    return ModuleConfig.from_yaml(MODULES_ROOT / module_name / "b1-module.yaml")


@pytest.mark.parametrize(
    "module_name,expected_command_prefix",
    [
        ("github-runners", "/gh-runners"),
        ("github-ai-agents", "/gh-agents"),
        ("github-bots", "/gh-bots"),
    ],
)
def test_github_module_manifest_parses(module_name, expected_command_prefix):
    config = _load(module_name)
    assert config.name == module_name
    assert config.type == ModuleType.deployment
    assert config.version == "1.0.0"
    assert len(config.skills) >= 2, f"{module_name} should declare at least 2 skills"
    assert len(config.commands) >= 3, f"{module_name} should declare at least 3 commands"
    assert all(
        c.name.startswith(expected_command_prefix) for c in config.commands
    ), f"all commands in {module_name} should start with {expected_command_prefix}"
    assert config.hooks.get("post-install") == "scripts/post-install.sh"


@pytest.mark.parametrize(
    "module_name,expected_files",
    [
        (
            "github-runners",
            [
                "context/best-practices.md",
                "context/conventions.md",
                "context/agent-capabilities.md",
                "scripts/post-install.sh",
                "scripts/runner-init.sh",
                "templates/runner-systemd.service.tmpl",
                "templates/runner-docker-compose.yml.tmpl",
                "templates/ephemeral-runner-workflow.yml.tmpl",
            ],
        ),
        (
            "github-ai-agents",
            [
                "context/best-practices.md",
                "context/conventions.md",
                "context/agent-capabilities.md",
                "scripts/post-install.sh",
                "scripts/agents-init.sh",
                "templates/claude-code-action.yml.tmpl",
                "templates/codex-action.yml.tmpl",
                "templates/agent-pr-review.yml.tmpl",
                "templates/AGENT_PERMISSIONS.md.tmpl",
            ],
        ),
        (
            "github-bots",
            [
                "context/best-practices.md",
                "context/conventions.md",
                "context/agent-capabilities.md",
                "scripts/post-install.sh",
                "scripts/bots-init.sh",
                "templates/dependabot.yml.tmpl",
                "templates/release-please.yml.tmpl",
                "templates/triage-labeler.yml.tmpl",
            ],
        ),
    ],
)
def test_github_module_artifacts_exist(module_name, expected_files):
    base = MODULES_ROOT / module_name
    missing = [f for f in expected_files if not (base / f).is_file()]
    assert not missing, f"{module_name} is missing: {missing}"


@pytest.mark.parametrize(
    "module_name,init_script",
    [
        ("github-runners", "scripts/runner-init.sh"),
        ("github-ai-agents", "scripts/agents-init.sh"),
        ("github-bots", "scripts/bots-init.sh"),
    ],
)
def test_init_scripts_are_executable(module_name, init_script):
    import os
    path = MODULES_ROOT / module_name / init_script
    assert path.is_file(), f"{path} missing"
    assert os.access(path, os.X_OK), f"{path} is not executable"
