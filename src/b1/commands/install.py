import typer
from pathlib import Path
from rich.console import Console

from b1.core.fetcher import ModuleFetcher
from b1.core.installer import ModuleInstaller

console = Console()

def install_cmd(
    source: str = typer.Argument(..., help="Git URL or local path to module target")
):
    """
    Equips the current project workspace with a specific development or deployment module.
    """
    project_dir = Path.cwd()
    if not (project_dir / ".agent").exists():
        console.print("[bold red]Error:[/bold red] Not a b1CodingTool project. Please run `b1 init` first.")
        raise typer.Exit(1)
        
    fetcher = ModuleFetcher()
    installer = ModuleInstaller(target_project_dir=project_dir)
    
    try:
        module_path = fetcher.fetch(source)
        installer.install(module_path)
    except Exception as e:
        console.print(f"[bold red]Installation Error:[/bold red] {e}")
        raise typer.Exit(1)
