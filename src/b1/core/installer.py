import shutil
import subprocess
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from b1.core.schema import ModuleConfig

console = Console()

class ModuleInstaller:
    def __init__(self, target_project_dir: Path):
        self.project_dir = target_project_dir
        self.modules_dir = self.project_dir / ".agent" / "modules"
        self.modules_dir.mkdir(parents=True, exist_ok=True)
        
    def install(self, source_path: Path):
        # Locate the yaml file
        yaml_path = source_path / "b1-module.yaml"
        if not yaml_path.exists():
            yaml_path = source_path / "module.yaml"
            if not yaml_path.exists():
                raise FileNotFoundError(f"No b1-module.yaml or module.yaml found in {source_path}")
                
        config = ModuleConfig.from_yaml(yaml_path)
        console.print(f"\\n[bold green]Installing Module:[/bold green] {config.name} (v{config.version})")
        
        target_mod_dir = self.modules_dir / config.name
        
        # 1. Copy files
        if target_mod_dir.exists():
            console.print(f"[yellow]Module {config.name} already installed. Overwriting...[/yellow]")
            shutil.rmtree(target_mod_dir)
            
        # Ignore .git folder when copying
        shutil.copytree(source_path, target_mod_dir, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        console.print(f"[green]\u2714[/green] Copied files to [blue]{target_mod_dir.relative_to(self.project_dir)}[/blue]")
        
        # 2. Run skill setup scripts
        if config.skills:
            console.print("\\n[bold]Preparing Skills[/bold]")
            for skill in config.skills:
                if skill.install_command:
                    self._run_skill_command(skill.name, skill.install_command, target_mod_dir)
                else:
                    console.print(f"[dim]  - {skill.name} (no setup required)[/dim]")
                    
        console.print(f"\\n[bold green]Successfully installed {config.name}![/bold green] \U0001f680")

    def _run_skill_command(self, name: str, command: str, execution_dir: Path):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Executing setup for [cyan]{name}[/cyan]...", total=None)
            
            try:
                # Run the command with access to shell
                subprocess.run(
                    command, 
                    cwd=execution_dir, 
                    shell=True, 
                    text=True, 
                    capture_output=True,
                    check=True
                )
                progress.update(task, description=f"[green]\u2714[/green] Setup complete for [cyan]{name}[/cyan]")
            except subprocess.CalledProcessError as e:
                progress.update(task, description=f"[red]\u2716[/red] Failed setup for [cyan]{name}[/cyan]")
                console.print(f"[red]Error Output:[/red]\\n{e.stderr}")
                # Don't halt the whole installation if one skill script fails, just note it.
