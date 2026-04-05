import typer
from typing import Optional, Annotated
from pathlib import Path
from rich.console import Console

from b1.core.scaffolder import scaffold_project
from b1.core.context_manager import setup_context

console = Console()

def init_cmd(
    path: Annotated[Optional[Path], typer.Argument(help="The directory to initialize (default: current directory)")] = None
):
    """
    Bootstraps a new or existing project with the b1CodingTool architecture.
    """
    if path is None:
        path = Path.cwd()
    
    path = path.resolve()
    
    console.print(f"[bold blue]Initializing b1CodingTool project at:[/bold blue] {path}")
    
    if not path.exists():
        console.print(f"[yellow]Directory {path} doesn't exist, creating it...[/yellow]")
        path.mkdir(parents=True, exist_ok=True)
        
    scaffold_project(path)
    setup_context(path)
    
    console.print("[bold green]Initialization complete![/bold green] \U0001f389")
