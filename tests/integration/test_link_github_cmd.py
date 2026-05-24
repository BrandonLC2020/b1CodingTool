from typer.testing import CliRunner
from b1.cli import app
from unittest.mock import patch
import subprocess
import json
import pytest

runner = CliRunner()

def test_link_github_cmd_success(tmp_path):
    with patch("b1.commands.link_github.subprocess.run") as mock_run:
        # Mock gh success
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({
            "owner": {"login": "brandon"},
            "name": "b1CodingTool",
            "defaultBranchRef": {"name": "main"}
        })
        
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["link-to-github-repo", "owner/repo"])
            assert result.exit_code == 0
            assert "Success" in result.stdout

def test_link_github_cmd_fallback_success(tmp_path):
    with patch("b1.commands.link_github.subprocess.run") as mock_run:
        # First call (gh) fails
        
        def side_effect(cmd, **kwargs):
            from unittest.mock import MagicMock
            mock_res = MagicMock()
            if cmd[0] == "gh":
                mock_res.returncode = 1
                mock_res.stdout = ""
                mock_res.stderr = "gh not found"
            elif cmd[0] == "git":
                mock_res.returncode = 0
                mock_res.stdout = "ref: refs/heads/develop	HEAD"
                mock_res.stderr = ""
            return mock_res
            
        mock_run.side_effect = side_effect
        
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            result = runner.invoke(app, ["link-to-github-repo", "owner/repo"])
            assert result.exit_code == 0
            assert "Warning: 'gh' CLI failed" in result.stdout
            assert "Success" in result.stdout
            
            # Verify config
            config_file = tmp_path / ".agents" / "config.yaml"
            assert config_file.exists()
            import yaml
            with open(config_file) as f:
                config_data = yaml.safe_load(f)
                assert config_data["github_owner"] == "owner"
                assert config_data["github_repo"] == "repo"
                assert config_data["default_branch"] == "develop"
                assert config_data["upstream_repo"] == "owner/repo"
