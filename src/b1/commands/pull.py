import typer
from pathlib import Path
from rich.console import Console

from b1.core.fetcher import ModuleFetcher
from b1.core.installer import ModuleInstaller

console = Console()

def pull_cmd():
    """
    Syncs local modules with the upstream version control.
    """
    project_dir = Path.cwd()
    modules_dir = project_dir / ".agent" / "modules"
    
    if not modules_dir.exists():
        console.print("[yellow]No modules currently installed in this project.[/yellow]")
        return
        
    fetcher = ModuleFetcher()
    installer = ModuleInstaller(target_project_dir=project_dir)
    
    installed_modules = [d for d in modules_dir.iterdir() if d.is_dir()]
    if not installed_modules:
        console.print("[yellow]No modules currently installed.[/yellow]")
        return
        
    for mod_path in installed_modules:
        console.print(f"\\n[bold blue]Pulling updates for {mod_path.name}...[/bold blue]")
        cache_target = fetcher.cache_dir / mod_path.name
        
        if cache_target.exists():
            try:
                updated_path = fetcher.fetch(str(cache_target))
                installer.install(updated_path)
            except Exception as e:
                console.print(f"[bold red]Failed to update {mod_path.name}:[/bold red] {e}")
        else:
            console.print(f"[yellow]Module {mod_path.name} not found in global cache. Skipping sync.[/yellow]")
            
    console.print("\\n[bold green]Pull sync complete![/bold green]")
