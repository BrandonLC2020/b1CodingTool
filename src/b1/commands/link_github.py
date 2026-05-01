import re
import subprocess
import json
from pathlib import Path
import typer
from rich.console import Console
from b1.core.config import B1Config

console = Console()

def extract_github_slug(input_str: str) -> tuple[str, str] | None:
    pattern = r"(?:github\.com[:/]|)([\w.-]+)/([\w.-]+?)(?:\.git|/|$)"
    match = re.search(pattern, input_str)
    if match:
        return match.group(1), match.group(2)
    return None

def link_github_cmd(repo_input: str):
    """
    Links the current project to a GitHub repository.
    """
    slug = extract_github_slug(repo_input)
    if not slug:
        console.print(f"[red]Error:[/red] Could not parse GitHub owner/repo from '{repo_input}'")
        raise typer.Exit(code=1)
        
    owner, repo = slug
    
    # 1. Try gh cli
    try:
        result = subprocess.run(
            ["gh", "repo", "view", f"{owner}/{repo}", "--json", "owner,name,defaultBranchRef"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            github_owner = data["owner"]["login"]
            github_repo = data["name"]
            default_branch = data["defaultBranchRef"]["name"]
        else:
            # 2. Fallback to git ls-remote to check existence and default branch
            console.print(f"[yellow]Warning:[/yellow] 'gh' CLI failed or not available. Falling back to 'git ls-remote'...")
            ls_remote = subprocess.run(
                ["git", "ls-remote", "--symref", f"https://github.com/{owner}/{repo}.git", "HEAD"],
                capture_output=True,
                text=True,
                check=False
            )
            if ls_remote.returncode == 0:
                # Example output: ref: refs/heads/main	HEAD
                match = re.search(r"ref: refs/heads/([\w.-]+)\s+HEAD", ls_remote.stdout)
                default_branch = match.group(1) if match else "main"
                github_owner = owner
                github_repo = repo
            else:
                console.print(f"[red]Error:[/red] Could not verify repository '{owner}/{repo}'.")
                raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Error:[/red] An unexpected error occurred: {e}")
        raise typer.Exit(code=1)

    # Update config
    project_dir = Path.cwd()
    config = B1Config.load(project_dir)
    config.github_owner = github_owner
    config.github_repo = github_repo
    config.default_branch = default_branch
    config.upstream_repo = f"{github_owner}/{github_repo}"
    config.save(project_dir)
    
    console.print(f"[green]Success![/green] Project linked to [bold]{github_owner}/{github_repo}[/bold] (default branch: [blue]{default_branch}[/blue])")
