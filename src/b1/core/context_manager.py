from pathlib import Path
from rich.console import Console

console = Console()

BASE_AGENT_MD = """# b1CodingTool: Global Context
This is the root `agents.md` file managed by b1CodingTool. 
It contains project-agnostic software development practices and general notes.

## General Guidelines
- Write clean, modular code.
- Include thoughtful documentation.
"""

PROJECT_AGENT_MD = """# b1CodingTool: Project Context
This is the project-specific `agents.md` context file.
It contains app logic, directory structures, and active tasks.

## Active Tasks
- Initial b1 setup

## Architecture Notes
- Follow the guidelines specified in the root `agents.md`.
"""

def setup_context(root_dir: Path):
    root_agent_path = root_dir / "agents.md"
    project_agent_dir = root_dir / ".agents" / "project"
    project_agent_path = project_agent_dir / "agents.md"
    
    # Root agents.md handling
    if root_agent_path.exists():
        content = root_agent_path.read_text(encoding="utf-8")
        if "b1CodingTool" not in content:
            console.print("[yellow]Appending b1CodingTool context to existing agents.md...[/yellow]")
            with open(root_agent_path, "a", encoding="utf-8") as f:
                f.write("\n\n" + BASE_AGENT_MD)
        else:
            console.print("[dim]Root agents.md already configured for b1CodingTool, skipping.[/dim]")
    else:
        root_agent_path.write_text(BASE_AGENT_MD, encoding="utf-8")
        console.print("[green]Created root agents.md.[/green]")

    # Project-specific agents.md handling
    project_agent_dir.mkdir(parents=True, exist_ok=True)
    if not project_agent_path.exists():
        project_agent_path.write_text(PROJECT_AGENT_MD, encoding="utf-8")
        console.print("[green]Created project-specific agents.md in .agents/project/.[/green]")
    else:
        console.print("[dim]Project-specific agents.md already exists, skipping.[/dim]")
