import typer
from pathlib import Path
from rich.console import Console

from b1.core.fetcher import ModuleFetcher
from b1.core.installer import ModuleInstaller
from b1.core.exceptions import ProjectError, B1Error

console = Console()

def install_cmd(
    source: str = typer.Argument(..., help="Git URL or local path to module target"),
    link: bool = typer.Option(False, "--link", "-l", help="Symlink the module instead of copying (useful for development)")
):
    """
    Equips the current project workspace with a specific development or deployment module.
    """
    project_dir = Path.cwd()
    if not (project_dir / ".agent").exists():
        raise ProjectError(
            "Not a b1CodingTool project.",
            suggestions=["Run `b1 init` to bootstrap the project structure.", "Ensure you are in the project root directory."]
        )
        
    fetcher = ModuleFetcher()
    installer = ModuleInstaller(target_project_dir=project_dir)
    
    module_path = fetcher.fetch(source)
    installer.install(module_path, link=link)
