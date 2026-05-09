import subprocess
import os
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from b1.core.schema import ModuleConfig

console = Console()

class HookEngine:
    """
    Handles discovery and execution of lifecycle hooks defined in b1 modules.
    """
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.modules_dir = self.project_dir / ".agent" / "modules"

    def run_hooks(self, hook_name: str, target_module: Optional[str] = None):
        """
        Runs the specified hook for all modules (or a specific module).
        """
        if not self.modules_dir.exists():
            return

        modules_to_scan = []
        if target_module:
            mod_path = self.modules_dir / target_module
            if mod_path.exists() and mod_path.is_dir():
                modules_to_scan.append(mod_path)
        else:
            modules_to_scan = [d for d in self.modules_dir.iterdir() if d.is_dir()]

        for mod_dir in modules_to_scan:
            # Load module config to find hooks
            yaml_path = mod_dir / "b1-module.yaml"
            if not yaml_path.exists():
                yaml_path = mod_dir / "module.yaml"
                
            if yaml_path.exists():
                try:
                    config = ModuleConfig.from_yaml(yaml_path)
                    if config.hooks and hook_name in config.hooks:
                        command = config.hooks[hook_name]
                        self._execute_hook(hook_name, command, mod_dir, config.name)
                except Exception as e:
                    console.print(f"[yellow]Warning: Could not load config for module {mod_dir.name} to run hooks: {e}[/yellow]")

    def _execute_hook(self, hook_name: str, command: str, module_dir: Path, module_name: str):
        """
        Executes a single hook command.
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Running [cyan]{hook_name}[/cyan] for [bold]{module_name}[/bold]...", total=None)

            try:
                # Resolve script path
                # If it's a relative path, assume it's relative to the module directory
                script_path = module_dir / command
                
                if script_path.exists():
                    # Make sure it's executable
                    os.chmod(script_path, 0o755)
                    
                    result = subprocess.run(
                        [str(script_path)],
                        cwd=self.project_dir, # Run hooks from project root
                        shell=False,
                        text=True,
                        capture_output=True,
                        check=True,
                        timeout=300 # 5 minute timeout
                    )
                    progress.update(task, description=f"[green]✔[/green] {hook_name} completed for [bold]{module_name}[/bold]")
                else:
                    # Fallback to shell command if script not found
                    result = subprocess.run(
                        command,
                        cwd=self.project_dir,
                        shell=True,
                        text=True,
                        capture_output=True,
                        check=True,
                        timeout=300
                    )
                    progress.update(task, description=f"[green]✔[/green] {hook_name} completed for [bold]{module_name}[/bold] (shell)")
                    
            except subprocess.TimeoutExpired:
                progress.update(task, description=f"[red]✖[/red] {hook_name} timed out for [bold]{module_name}[/bold]")
                console.print(f"[red]Error:[/red] Hook timed out after 300s: {command}")
            except subprocess.CalledProcessError as e:
                progress.update(task, description=f"[red]✖[/red] {hook_name} failed for [bold]{module_name}[/bold]")
                if e.stdout:
                    console.print(f"[dim]Output:[/dim]\n{e.stdout}")
                if e.stderr:
                    console.print(f"[red]Error Output:[/red]\n{e.stderr}")
