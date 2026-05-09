import typer
import yaml
import shutil
import tempfile
from pathlib import Path
from rich.console import Console
from rich.table import Table
from typing import Optional

from b1.core.config import B1Config
from b1.core.skillsmp import SkillsMPClient, SkillsMPSkill
from b1.core.fetcher import ModuleFetcher
from b1.core.installer import ModuleInstaller
from b1.core.exceptions import B1Error, ProjectError

app = typer.Typer(help="Manage community skills from skillsmp.com", no_args_is_help=True)
console = Console()

@app.command(name="search")
def skill_search(
    query: str = typer.Argument(..., help="Search query for skills"),
    limit: int = typer.Option(10, "--limit", "-l", help="Number of results to show")
):
    """
    Search for community skills on skillsmp.com.
    """
    config = B1Config.load(Path.cwd())
    client = SkillsMPClient(api_key=config.skillsmp_api_key)
    
    with console.status(f"[bold blue]Searching skillsmp.com for '{query}'..."):
        try:
            skills = client.search(query, limit=limit)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            raise typer.Exit(1)

    if not skills:
        console.print(f"[yellow]No skills found for '{query}'.[/yellow]")
        return

    table = Table(title=f"SkillsMP Results for '{query}'")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    table.add_column("Author", style="magenta")
    table.add_column("Description", style="white")
    table.add_column("Stars", style="yellow")

    for skill in skills:
        desc = skill.description or ""
        if len(desc) > 80:
            desc = desc[:77] + "..."
        table.add_row(
            skill.id,
            skill.name,
            skill.author,
            desc,
            str(skill.stars)
        )

    console.print(table)
    console.print(f"\n[dim]Use 'b1 skill install <ID>' to add a skill to your project.[/dim]")

@app.command(name="install")
def skill_install(
    skill_id: str = typer.Argument(..., help="The ID of the skill to install")
):
    """
    Installs a community skill from skillsmp.com into the current project.
    """
    project_dir = Path.cwd()
    if not (project_dir / ".agent").exists():
        raise ProjectError(
            "Not a b1CodingTool project.",
            suggestions=["Run `b1 init` to bootstrap the project structure."]
        )

    config = B1Config.load(project_dir)
    client = SkillsMPClient(api_key=config.skillsmp_api_key)
    
    with console.status(f"[bold blue]Fetching skill metadata for '{skill_id}'..."):
        skill = client.get_by_id(skill_id)
        
    if not skill:
        console.print(f"[bold red]Skill not found:[/bold red] {skill_id}")
        raise typer.Exit(1)

    console.print(f"[bold green]Found skill:[/bold green] {skill.name} by {skill.author}")
    
    fetcher = ModuleFetcher()
    installer = ModuleInstaller(target_project_dir=project_dir)
    
    try:
        # 1. Fetch the source (handle GitHub subpaths)
        source_path = fetcher.fetch(skill.github_url)
        
        # 2. Check if it already has a b1-module.yaml
        yaml_path = source_path / "b1-module.yaml"
        if not yaml_path.exists():
            yaml_path = source_path / "module.yaml"
            
        if not yaml_path.exists():
            # 3. Create a synthetic module config
            console.print("[dim]Generating synthetic b1-module.yaml for community skill...[/dim]")
            
            # Create a temporary directory to host the synthetic module
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir)
                
                # Copy everything from source to tmp
                if source_path.is_file():
                    # If it's just a file (e.g. SKILL.md), put it in context/
                    context_dir = tmp_path / "context"
                    context_dir.mkdir()
                    shutil.copy2(source_path, context_dir / source_path.name)
                else:
                    # It's a directory
                    shutil.copytree(source_path, tmp_path, dirs_exist_ok=True)
                    # Move all .md files to context/ if not already there
                    context_dir = tmp_path / "context"
                    if not context_dir.exists():
                        context_dir.mkdir()
                    for md_file in tmp_path.glob("*.md"):
                        if md_file.parent != context_dir:
                            shutil.move(str(md_file), str(context_dir / md_file.name))
                
                # Create b1-module.yaml
                module_name = f"community-{skill.name}"
                # Clean name
                module_name = "".join(c if c.isalnum() or c in "-_" else "-" for c in module_name).lower()
                
                synthetic_config = {
                    "name": module_name,
                    "version": "1.0.0",
                    "type": "cross_cutting",
                    "description": f"Community skill: {skill.description}",
                    "skills": [
                        {
                            "name": skill.name,
                            "description": skill.description
                        }
                    ]
                }
                
                with open(tmp_path / "b1-module.yaml", "w", encoding="utf-8") as f:
                    yaml.safe_dump(synthetic_config, f)
                
                # 4. Install from tmp
                installer.install(tmp_path)
        else:
            # Already a valid b1 module
            installer.install(source_path)
            
    except Exception as e:
        console.print(f"[bold red]Installation failed:[/bold red] {e}")
        raise typer.Exit(1)
