import typer
from rich.console import Console

from b1.commands.init import init_cmd
from b1.commands.install import install_cmd

app = typer.Typer(
    name="b1",
    help="b1CodingTool: Agent-agnostic development environment manager.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()

app.command(name="init")(init_cmd)
app.command(name="install")(install_cmd)

def main():
    app()
