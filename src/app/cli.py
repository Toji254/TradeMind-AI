from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from src.analysis.engine import AnalysisEngine
from src.analysis.sample_data import sample_trades
from src.app.config import settings
from src.storage.local_db import init_db

app = typer.Typer(help="TradeMind AI command line interface")
console = Console()


@app.command()
def doctor() -> None:
    """Run a basic project health check."""
    table = Table(title="TradeMind AI Doctor")
    table.add_column("Check")
    table.add_column("Value")
    table.add_row("Environment", settings.env)
    table.add_row("Database Path", str(settings.db_path))
    table.add_row("Binance API Key Configured", "yes" if settings.binance_api_key else "no")
    console.print(table)


@app.command()
def init() -> None:
    """Initialize the local database."""
    init_db(settings.db_path)
    console.print(f"[green]Initialized database at {settings.db_path}[/green]")


@app.command()
def demo() -> None:
    """Run sample behavioral analysis using demo trades."""
    engine = AnalysisEngine()
    results = engine.run(sample_trades())
    console.print("[bold cyan]TradeMind AI Demo Analysis[/bold cyan]")
    for result in results:
        console.print(f"\n[bold]{result.pattern}[/bold] ({result.confidence:.0%})")
        console.print(result.summary)
        if result.coaching:
            for suggestion in result.coaching:
                console.print(f"- {suggestion}")


if __name__ == "__main__":
    app()
