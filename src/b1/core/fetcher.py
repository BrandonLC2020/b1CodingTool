import subprocess
import os
from pathlib import Path
from rich.console import Console
from b1.core.exceptions import NetworkError

console = Console()

class ModuleFetcher:
    def __init__(self, timeout: int = 60):
        self.cache_dir = Path.home() / ".b1" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        
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
        if source.startswith("http") or source.startswith("git@") or source.startswith("file://"):
            module_name = source.split("/")[-1].replace(".git", "")
            target_path = self.cache_dir / module_name
            
            if target_path.exists():
                console.print(f"[dim]Module {module_name} already in cache. Pulling latest...[/dim]")
                try:
                    subprocess.run(
                        ["git", "-C", str(target_path), "pull"], 
                        check=True, 
                        capture_output=True,
                        timeout=self.timeout
                    )
                except subprocess.TimeoutExpired:
                    raise NetworkError(
                        f"Connection timed out while pulling {source}",
                        suggestions=[
                            "Check your internet connection.",
                            "The git server might be slow or unresponsive.",
                            f"Try increasing the timeout (current: {self.timeout}s)."
                        ]
                    )
                except subprocess.CalledProcessError as e:
                    stderr = e.stderr.decode('utf-8')
                    suggestions = [
                        "Verify you have access to the repository.",
                        "Check if the repository URL is correct."
                    ]
                    if "SSL" in stderr or "certificate" in stderr:
                        suggestions.append("Check your SSL certificate configuration.")
                        suggestions.append("Try setting GIT_SSL_NO_VERIFY=true if you are behind a corporate proxy (use with caution).")
                    
                    raise NetworkError(
                        f"Failed to pull latest from {source}\nError: {stderr.strip()}",
                        suggestions=suggestions
                    )
                return target_path
            
            console.print(f"[blue]Cloning module from {source}...[/blue]")
            try:
                subprocess.run(
                    ["git", "clone", source, str(target_path)], 
                    check=True, 
                    capture_output=True,
                    timeout=self.timeout
                )
            except subprocess.TimeoutExpired:
                raise NetworkError(
                    f"Connection timed out while cloning {source}",
                    suggestions=[
                        "Check your internet connection.",
                        "Verify the repository URL exists.",
                        f"Try increasing the timeout (current: {self.timeout}s)."
                    ]
                )
            except subprocess.CalledProcessError as e:
                stderr = e.stderr.decode('utf-8')
                suggestions = [
                    "Verify you have access to the repository.",
                    "Check if the repository URL is correct."
                ]
                if "SSL" in stderr or "certificate" in stderr:
                    suggestions.append("Check your SSL certificate configuration.")
                    suggestions.append("Try setting GIT_SSL_NO_VERIFY=true if you are behind a corporate proxy (use with caution).")
                
                raise NetworkError(
                    f"Failed to clone {source}\nError: {stderr.strip()}",
                    suggestions=suggestions
                )
                
            return target_path
            
        raise ValueError(f"Invalid module source or not found locally: {source}")
