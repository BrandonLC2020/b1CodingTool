from b1.commands.init import init_cmd
from b1.commands.install import install_cmd
from b1.commands.pull import pull_cmd
from b1.commands.push import push_cmd
from b1.commands.pair import pair_cmd
from b1.commands.dashboard import dashboard_cmd

app = typer.Typer(
    name="b1",
    help="b1CodingTool: Agent-agnostic development environment manager.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()

app.command(name="init")(init_cmd)
app.command(name="install")(install_cmd)
app.command(name="pull")(pull_cmd)
app.command(name="push")(push_cmd)
app.command(name="pair")(pair_cmd)
app.command(name="dashboard")(dashboard_cmd)

def main():
    app()
