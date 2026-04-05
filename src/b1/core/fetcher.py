import subprocess
from pathlib import Path
from rich.console import Console

console = Console()

class ModuleFetcher:
    def __init__(self):
        self.cache_dir = Path.home() / ".b1" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def fetch(self, source: str) -> Path:
        """
        Takes a source (either a git url or local path).
        Returns the pathlib.Path to the prepared module directory.
        """
        # If it's a local path
        local_path = Path(source).expanduser().resolve()
        if local_path.exists() and local_path.is_dir():
            if (local_path / "b1-module.yaml").exists() or (local_path / "module.yaml").exists():
                return local_path
                
        # If it looks like a Git URL
        if source.startswith("http") or source.startswith("git@"):
            module_name = source.split("/")[-1].replace(".git", "")
            target_path = self.cache_dir / module_name
            
            if target_path.exists():
                console.print(f"[dim]Module {module_name} already in cache. Pulling latest...[/dim]")
                try:
                    subprocess.run(["git", "-C", str(target_path), "pull"], check=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    console.print(f"[bold red]Failed to pull latest from {source}[/bold red]")
                    console.print(e.stderr.decode('utf-8'))
                    raise
                return target_path
            
            console.print(f"[blue]Cloning module from {source}...[/blue]")
            try:
                subprocess.run(["git", "clone", source, str(target_path)], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                console.print(f"[bold red]Failed to clone {source}[/bold red]")
                console.print(e.stderr.decode('utf-8'))
                raise
                
            return target_path
            
        raise ValueError(f"Invalid module source or not found locally: {source}")
