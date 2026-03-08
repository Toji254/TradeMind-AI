from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from src.analysis.engine import AnalysisEngine
from src.analysis.sample_data import sample_trades
from src.app.config import settings
from src.connectors.binance_client import BinanceClient, BinanceCredentials
from src.storage.local_db import init_db, upsert_trades

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
    table.add_row("Spot API Configured", "yes" if settings.binance_spot_api_key else "no")
    table.add_row("Futures API Configured", "yes" if settings.binance_futures_api_key else "no")
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


@app.command("binance-ping")
def binance_ping(market: str = typer.Option("spot", help="spot or futures")) -> None:
    """Validate Binance testnet connectivity."""
    client = _build_client(market)
    client.ping()
    console.print(f"[green]{market} testnet ping succeeded[/green]")


@app.command("sync-binance")
def sync_binance(
    symbol: str = typer.Option(..., help="Trading pair symbol, e.g. BTCUSDT"),
    limit: int = typer.Option(50, min=1, max=1000),
    market: str = typer.Option("spot", help="spot or futures"),
) -> None:
    """Fetch trades from Binance and store them locally."""
    if market != "spot":
        raise typer.BadParameter("Futures sync is not implemented yet; config support exists but sync starts with spot.")

    client = _build_client(market)
    trades = client.fetch_and_normalize_trades(symbol=symbol, limit=limit)
    inserted = upsert_trades(settings.db_path, trades)
    console.print(f"[green]Synced {inserted} {market} trades for {symbol} into {settings.db_path}[/green]")


@app.command("binance-account")
def binance_account(market: str = typer.Option("spot", help="spot or futures")) -> None:
    """Fetch a lightweight account snapshot from Binance."""
    if market != "spot":
        raise typer.BadParameter("Futures account snapshot is not implemented yet.")

    client = _build_client(market)
    account = client.get_account()
    balances = account.get("balances", [])
    non_zero = [b for b in balances if float(b.get("free", 0)) or float(b.get("locked", 0))]

    table = Table(title=f"Binance {market.title()} Account Snapshot")
    table.add_column("Can Trade")
    table.add_column("Can Withdraw")
    table.add_column("Non-zero Balances")
    table.add_row(str(account.get("canTrade")), str(account.get("canWithdraw")), str(len(non_zero)))
    console.print(table)


def _build_client(market: str) -> BinanceClient:
    market = market.lower().strip()
    if market == "spot":
        if not settings.binance_spot_api_key or not settings.binance_spot_api_secret:
            raise typer.BadParameter("Spot API credentials are missing in local environment config.")
        credentials = BinanceCredentials(
            api_key=settings.binance_spot_api_key,
            api_secret=settings.binance_spot_api_secret,
            base_url=settings.binance_spot_base_url,
        )
        return BinanceClient(credentials)

    if market == "futures":
        if not settings.binance_futures_api_key or not settings.binance_futures_api_secret:
            raise typer.BadParameter("Futures API credentials are missing in local environment config.")
        credentials = BinanceCredentials(
            api_key=settings.binance_futures_api_key,
            api_secret=settings.binance_futures_api_secret,
            base_url=settings.binance_futures_base_url,
        )
        return BinanceClient(credentials)

    raise typer.BadParameter("market must be 'spot' or 'futures'")


if __name__ == "__main__":
    app()
