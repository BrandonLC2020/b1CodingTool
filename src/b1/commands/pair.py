import typer
import time
from pathlib import Path
from rich.console import Console

from b1.core.config import B1Config
from b1.core.compiler import ContextCompiler
from b1.core.translator import AgentTranslator

console = Console()

def pair_cmd():
    """
    Ensures cross-agent parity across the workspace by translating root settings.
    """
    project_dir = Path.cwd()
    if not (project_dir / ".agent").exists():
        console.print("[bold red]Project not initialized. Run b1 init.[/bold red]")
        raise typer.Exit(1)
        
    config = B1Config.load(project_dir)
    
    if not config.active_agents:
        console.print("[blue]Configuring active agents...[/blue]")
        agent_input = typer.prompt("Which agents do you want to target? (comma separated, e.g. CLAUDE,GEMINI,CODEX)", default="CLAUDE,GEMINI,CODEX")
        agents = [a.strip().upper() for a in agent_input.split(",") if a.strip()]
        config.active_agents = agents
        config.save(project_dir)
        console.print(f"[dim]Saved active agents to config: {', '.join(agents)}[/dim]")
        
    compiler = ContextCompiler(project_dir)
    translator = AgentTranslator(project_dir)
    
    console.print("[bold blue]Compiling contexts...[/bold blue]")
    compiled_text = compiler.compile()
    
    if not compiled_text:
        console.print("[yellow]No context found to compile.[/yellow]")
        return
        
    console.print(f"[blue]Writing configurations for:[/blue] {', '.join(config.active_agents)}")
    translator.generate_files(config.active_agents, compiled_text)
    
    console.print("\\n[bold green]Cross-agent parity synchronization complete![/bold green] \U0001f504")
