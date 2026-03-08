from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from src.analysis.engine import AnalysisEngine
from src.analysis.sample_data import sample_trades
from src.app.config import settings
from src.app.services import TradeMindService
from src.coaching.coach import Coach
from src.coaching.interventions import build_intervention_plan
from src.connectors.binance_client import BinanceClient, BinanceCredentials
from src.reports.summary import render_summary
from src.storage.local_db import (
    add_journal_entry,
    init_db,
    list_symbols,
    load_journal_entries,
    load_trades,
)

app = typer.Typer(help="TradeMind AI command line interface")
console = Console()
service = TradeMindService()


@app.command()
def doctor() -> None:
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
    init_db(settings.db_path)
    console.print(f"[green]Initialized database at {settings.db_path}[/green]")


@app.command()
def demo() -> None:
    engine = AnalysisEngine()
    coach = Coach()
    trades = sample_trades()
    results = engine.run(trades)
    console.print("[bold cyan]TradeMind AI Demo Analysis[/bold cyan]")
    console.print(coach.summarize(trades, results))


@app.command("serve-web")
def serve_web(host: str = typer.Option("127.0.0.1"), port: int = typer.Option(8000)) -> None:
    import uvicorn

    uvicorn.run("src.web.app:app", host=host, port=port, reload=False)


@app.command("binance-ping")
def binance_ping(market: str = typer.Option("spot", help="spot or futures")) -> None:
    client = _build_client(market)
    client.ping(market=market)
    console.print(f"[green]{market} testnet ping succeeded[/green]")


@app.command("sync-binance")
def sync_binance(
    symbol: str = typer.Option(..., help="Trading pair symbol, e.g. BTCUSDT"),
    limit: int = typer.Option(50, min=1, max=1000),
    market: str = typer.Option("spot", help="spot or futures"),
) -> None:
    inserted = service.sync_symbol(symbol=symbol, limit=limit, market=market)
    console.print(f"[green]Synced {inserted} {market} trades for {symbol} into {settings.db_path}[/green]")


@app.command("sync-and-analyze")
def sync_and_analyze(
    symbol: str = typer.Option(..., help="Trading pair symbol, e.g. BTCUSDT"),
    limit: int = typer.Option(100, min=1, max=1000),
    market: str = typer.Option("spot", help="spot or futures"),
) -> None:
    sync_binance(symbol=symbol, limit=limit, market=market)
    analyze_local(symbol=symbol, limit=limit, as_json=False)


@app.command("binance-account")
def binance_account(market: str = typer.Option("spot", help="spot or futures"), as_json: bool = typer.Option(False, "--json")) -> None:
    snapshot = service.get_account_snapshot(market=market)
    if as_json:
        console.print_json(json.dumps(snapshot))
        return

    table = Table(title=f"Binance {market.title()} Account Snapshot")
    table.add_column("Metric")
    table.add_column("Value")
    for key, value in snapshot.items():
        table.add_row(str(key), str(value))
    console.print(table)


@app.command("profit-status")
def profit_status(market: str = typer.Option("spot", help="spot or futures")) -> None:
    snapshot = service.get_account_snapshot(market=market)
    if market == "futures":
        console.print(
            f"Wallet: {snapshot['wallet_balance']:.2f} USDT | Unrealized: {snapshot['unrealized_profit']:.2f} USDT | Available: {snapshot['available_balance']:.2f} USDT"
        )
    else:
        console.print(
            f"Estimated spot account value: ~{snapshot['estimated_total_usdt']:.2f} USDT across {snapshot['asset_count']} assets"
        )


@app.command("trader-brief")
def trader_brief(
    symbol: str | None = typer.Option(None, help="Optional symbol filter"),
    limit: int = typer.Option(100, min=1, max=5000),
    market: str = typer.Option("spot", help="spot or futures"),
) -> None:
    console.print(service.build_trader_brief(symbol=symbol, limit=limit, market=market))


@app.command("message-preview")
def message_preview(
    symbol: str | None = typer.Option(None),
    limit: int = typer.Option(100, min=1, max=5000),
    market: str = typer.Option("spot", help="spot or futures"),
) -> None:
    console.print(service.build_trader_brief(symbol=symbol, limit=limit, market=market))


@app.command("openclaw-prompt")
def openclaw_prompt(
    symbol: str | None = typer.Option(None),
    limit: int = typer.Option(100, min=1, max=5000),
    market: str = typer.Option("spot", help="spot or futures"),
) -> None:
    brief = service.build_trader_brief(symbol=symbol, limit=limit, market=market)
    console.print("Use this as the trader-facing OpenClaw message:\n\n" + brief)


@app.command("list-symbols")
def local_symbols() -> None:
    symbols = list_symbols(settings.db_path)
    table = Table(title="Local Symbols")
    table.add_column("Symbol")
    table.add_column("Trades")
    for symbol, count in symbols:
        table.add_row(symbol, str(count))
    if not symbols:
        table.add_row("(none)", "0")
    console.print(table)


@app.command("journal-add")
def journal_add(
    text: str = typer.Argument(..., help="Journal entry text"),
    tag: str = typer.Option("general", help="Tag such as pretrade, posttrade, fear, confidence"),
) -> None:
    entry_id = add_journal_entry(settings.db_path, tag=tag, text=text)
    console.print(f"[green]Saved journal entry #{entry_id}[/green]")


@app.command("journal-list")
def journal_list(limit: int = typer.Option(10, min=1, max=100), tag: str | None = typer.Option(None)) -> None:
    entries = load_journal_entries(settings.db_path, limit=limit, tag=tag)
    table = Table(title="Journal Entries")
    table.add_column("ID")
    table.add_column("Created")
    table.add_column("Tag")
    table.add_column("Sentiment")
    table.add_column("Text")
    for entry in entries:
        table.add_row(str(entry.entry_id), entry.created_at.isoformat(timespec="seconds"), entry.tag, f"{entry.sentiment_compound:.2f}", entry.text)
    if not entries:
        table.add_row("-", "-", "-", "-", "No journal entries yet")
    console.print(table)


@app.command("coaching-plan")
def coaching_plan(symbol: str | None = typer.Option(None), limit: int = typer.Option(100, min=1, max=5000)) -> None:
    trades = load_trades(settings.db_path, symbol=symbol, limit=limit)
    results = AnalysisEngine().run(trades)
    plan = build_intervention_plan(results)
    console.print("[bold cyan]TradeMind AI Coaching Plan[/bold cyan]")
    if symbol:
        console.print(f"Symbol filter: [bold]{symbol.upper()}[/bold]")
    if not plan:
        console.print("No active guardrail plan suggested yet. Sync more trades or add more varied trading behavior.")
        return
    for item in plan:
        console.print(f"- {item}")


@app.command("analyze-local")
def analyze_local(
    symbol: str | None = typer.Option(None, help="Optional symbol filter, e.g. BTCUSDT"),
    limit: int = typer.Option(100, min=1, max=5000),
    as_json: bool = typer.Option(False, "--json", help="Output machine-readable JSON summary"),
) -> None:
    trades = load_trades(settings.db_path, symbol=symbol, limit=limit)
    engine = AnalysisEngine()
    coach = Coach()
    journal_entries = load_journal_entries(settings.db_path, limit=5)
    results = engine.run(trades)

    if as_json:
        console.print_json(json.dumps(render_summary(results, trades)))
        return

    console.print("[bold cyan]TradeMind AI Local Analysis[/bold cyan]")
    if symbol:
        console.print(f"Symbol filter: [bold]{symbol.upper()}[/bold]")
    console.print(coach.summarize(trades, results, journal_entries=journal_entries))


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
