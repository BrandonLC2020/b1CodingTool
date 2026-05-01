from typer.testing import CliRunner
from b1.cli import app
from b1.core.config import B1Config
import yaml

runner = CliRunner()

def test_link_clickup_success(tmp_path):
    # Setup mock project
    dot_agent = tmp_path / ".agent"
    dot_agent.mkdir()
    (dot_agent / "config.yaml").write_text("upstream_repo: ''")
    
    import os
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        result = runner.invoke(app, ["link-to-clickup-list", "901414778471"])
        assert result.exit_code == 0
        assert "Project linked to ClickUp list" in result.stdout
        
        config = B1Config.load(tmp_path)
        assert config.clickup_list_id == "901414778471"
    finally:
        os.chdir(old_cwd)
