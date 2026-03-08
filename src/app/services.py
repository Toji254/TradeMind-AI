from __future__ import annotations

from collections import defaultdict

from src.analysis.engine import AnalysisEngine
from src.app.config import settings
from src.coaching.coach import Coach
from src.connectors.binance_client import BinanceClient, BinanceCredentials
from src.reports.summary import render_summary
from src.storage.local_db import load_journal_entries, load_trades, upsert_trades


class TradeMindService:
    def __init__(self) -> None:
        self.engine = AnalysisEngine()
        self.coach = Coach()

    def analyze_local(self, symbol: str | None = None, limit: int = 100) -> dict:
        trades = load_trades(settings.db_path, symbol=symbol, limit=limit)
        journal_entries = load_journal_entries(settings.db_path, limit=8)
        results = self.engine.run(trades)
        summary = render_summary(results, trades)
        summary["coach_text"] = self.coach.summarize(trades, results, journal_entries=journal_entries)
        summary["journal_entries"] = [
            {
                "entry_id": entry.entry_id,
                "created_at": entry.created_at.isoformat(timespec="seconds"),
                "tag": entry.tag,
                "text": entry.text,
                "sentiment_compound": entry.sentiment_compound,
            }
            for entry in journal_entries
        ]
        summary["selected_symbol"] = symbol.upper() if symbol else None
        summary["symbols_available"] = sorted(summary.get("symbols", []))
        summary["charts"] = self._build_chart_data(trades)
        return summary

    def sync_symbol(self, symbol: str, limit: int = 100, market: str = "spot") -> int:
        client = self._build_client(market)
        trades = client.fetch_and_normalize_trades(symbol=symbol, limit=limit, market=market)
        return upsert_trades(settings.db_path, trades)

    def _build_client(self, market: str) -> BinanceClient:
        if market == "spot":
            if not settings.binance_spot_api_key or not settings.binance_spot_api_secret:
                raise ValueError("Spot API credentials are missing.")
            return BinanceClient(
                BinanceCredentials(
                    api_key=settings.binance_spot_api_key,
                    api_secret=settings.binance_spot_api_secret,
                    base_url=settings.binance_spot_base_url,
                )
            )
        if market == "futures":
            if not settings.binance_futures_api_key or not settings.binance_futures_api_secret:
                raise ValueError("Futures API credentials are missing.")
            return BinanceClient(
                BinanceCredentials(
                    api_key=settings.binance_futures_api_key,
                    api_secret=settings.binance_futures_api_secret,
                    base_url=settings.binance_futures_base_url,
                )
            )
        raise ValueError("Unsupported market")

    def _build_chart_data(self, trades: list) -> dict:
        equity_curve = []
        cumulative = 0.0
        for index, trade in enumerate(trades, start=1):
            cumulative += trade.pnl
            equity_curve.append({"x": index, "value": round(cumulative, 4), "label": trade.timestamp.isoformat(timespec='seconds')})

        hourly = defaultdict(int)
        side_mix = {"BUY": 0, "SELL": 0}
        for trade in trades:
            hourly[trade.hour_utc] += 1
            side_mix[trade.side.upper()] = side_mix.get(trade.side.upper(), 0) + 1

        return {
            "equity_curve": equity_curve,
            "hourly_activity": [{"hour": hour, "count": hourly.get(hour, 0)} for hour in range(24)],
            "side_mix": [{"label": key, "value": value} for key, value in side_mix.items() if value > 0],
        }
