import typer
import subprocess
import time
from pathlib import Path
from rich.console import Console
import shutil

from b1.core.config import B1Config

console = Console()

def push_cmd():
    """
    Scans project-specific agent files and drafts a Pull Request to upstream.
    """
    project_dir = Path.cwd()
    if not (project_dir / ".agent").exists():
        console.print("[bold red]Project not initialized. Run b1 init.[/bold red]")
        raise typer.Exit(1)
        
    config = B1Config.load(project_dir)
    
    if not config.upstream_repo:
        repo = typer.prompt("No upstream repository configured. Enter the upstream GitHub repo (e.g. org/repo)")
        config.upstream_repo = repo
        config.save(project_dir)
        console.print(f"[green]Saved upstream config to .agent/config.yaml[/green]")
        
    if not shutil.which("gh"):
        console.print("[bold red]GitHub CLI (gh) is not installed. Please install it to use b1 push.[/bold red]")
        raise typer.Exit(1)
        
    branch_name = f"b1-learnings-{int(time.time())}"
    console.print(f"[bold blue]Checking out new branch {branch_name}...[/bold blue]")
    try:
        subprocess.run(["git", "checkout", "-b", branch_name], check=True, capture_output=True)
        
        console.print("[dim]Staging agent contexts...[/dim]")
        subprocess.run(["git", "add", ".agent/"], check=True, capture_output=True)
        
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if not status.stdout.strip():
            console.print("[yellow]No modifications detected in .agent/. Nothing to push.[/yellow]")
            subprocess.run(["git", "checkout", "-"], check=True, capture_output=True)
            subprocess.run(["git", "branch", "-d", branch_name], check=True, capture_output=True)
            return

        subprocess.run(["git", "commit", "-m", "chore: drafted generalized learnings from project context"], check=True, capture_output=True)
        
        console.print(f"[blue]Pushing branch to origin...[/blue]")
        subprocess.run(["git", "push", "-u", "origin", branch_name], check=True, capture_output=True)
        
        console.print(f"\\n[bold magenta]Drafting Pull Request to {config.upstream_repo}...[/bold magenta]")
        
        pr_command = [
            "gh", "pr", "create", 
            "--repo", config.upstream_repo,
            "--title", "Draft Generalized Learnings", 
            "--body", "This PR forwards project-specific guidelines and logic detected in the agent context files for community/team review.",
            "--draft"
        ]
        
        pr_result = subprocess.run(pr_command, check=True, capture_output=True, text=True)
        
        console.print(f"\\n[bold green]Success! Pull Request Drafted:[/bold green] {pr_result.stdout.strip()}")
        
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Git/GH Error:[/bold red]")
        err_msg = e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else (e.stderr or e.stdout)
        console.print(err_msg)
        raise typer.Exit(1)
