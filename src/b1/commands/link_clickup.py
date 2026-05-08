import typer
import re
from pathlib import Path
from rich.console import Console
from typing import Annotated

from b1.core.config import B1Config

console = Console()

def extract_list_id(input_str: str) -> str | None:
    match = re.search(r"li/(\d{11,13})(?:\?|$)", input_str)
    if match:
        return match.group(1)
    match = re.search(r"^(\d{11,13})$", input_str)
    return match.group(1) if match else None

def run_link_clickup(input_str: str) -> str:
    """
    Core logic to link the project to a ClickUp list.
    Returns the list_id or raises an exception.
    """
    list_id = extract_list_id(input_str)
    if not list_id:
        raise ValueError("Could not extract a valid ClickUp List ID.")

    project_dir = Path.cwd()
    config = B1Config.load(project_dir)
    config.clickup_list_id = list_id
    config.save(project_dir)
    return list_id

def link_clickup_cmd(
    input_str: Annotated[str, typer.Argument(help="The ClickUp List URL or ID")]
):
    """
    Links the project to a ClickUp list for task management.
    """
    try:
        list_id = run_link_clickup(input_str)
        console.print(f"[bold green]Success![/bold green] Project linked to ClickUp list: [blue]{list_id}[/blue]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)
