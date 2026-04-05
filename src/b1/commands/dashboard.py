import typer
import uvicorn
import webbrowser
from threading import Timer
from rich.console import Console

from b1.server.main import app

console = Console()

def open_browser(url: str):
    webbrowser.open(url)

def dashboard_cmd(
    port: int = typer.Option(8000, help="Port to run the dashboard on"),
    host: str = typer.Option("127.0.0.1", help="Host to bind the server to"),
    no_browser: bool = typer.Option(False, "--no-browser", help="Do not open the browser automatically")
):
    """
    Launches the b1CodingTool local dashboard.
    """
    url = f"http://{host}:{port}"
    
    # Schedule the browser open after server starts
    if not no_browser:
        Timer(1.5, open_browser, args=(url,)).start()
        
    console.print(f"\\n[bold green]Launching b1CodingTool Dashboard...[/bold green]")
    console.print(f"Running on [blue]{url}[/blue]")
    console.print("[dim]Press Ctrl+C to stop the dashboard server.[/dim]\\n")
    
    uvicorn.run(app, host=host, port=port, log_level="warning")
