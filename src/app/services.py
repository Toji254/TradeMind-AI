from __future__ import annotations

from collections import defaultdict
import asyncio

from src.analysis.engine import AnalysisEngine
from src.analysis.analysis_engine import analyze_patterns, render_coaching_summary
from src.app.config import settings
from src.coaching.coach import Coach
from src.connectors.binance_client import BinanceClient, BinanceCredentials
from src.connectors.market_data import MarketDataService
from src.connectors.telegram_bot import TelegramBotService
from src.reports.account import summarize_futures_account, summarize_spot_account
from src.reports.messaging import render_trader_brief
from src.reports.summary import render_summary
from src.storage.local_db import load_journal_entries, load_trades, upsert_trades


class TradeMindService:
    def __init__(self) -> None:
        self.engine = AnalysisEngine()
        self.coach = Coach()
        self.market_data = MarketDataService()
        self.telegram = TelegramBotService()

    def analyze_local(self, symbol: str | None = None, limit: int = 100) -> dict:
        trades = load_trades(settings.db_path, symbol=symbol, limit=limit)
        journal_entries = load_journal_entries(settings.db_path, limit=8)
        results = self.engine.run(trades)
        summary = render_summary(results, trades)

        # Legacy coach text (kept for compatibility)
        legacy_coach = self.coach.summarize(trades, results, journal_entries=journal_entries)
        summary["legacy_coach_text"] = legacy_coach

        # New FOMO / panic analysis engine
        try:
            pattern_payload = [
                {
                    "price": t.price,
                    "time": t.timestamp.isoformat(),
                    "isBuyer": t.side.upper() == "BUY",
                }
                for t in trades
            ]
            pattern_result = analyze_patterns(pattern_payload)
        except Exception:
            pattern_result = {
                "total_trades": len(trades),
                "fomo_buy_count": 0,
                "fomo_buy_pct": 0.0,
                "panic_sell_count": 0,
                "panic_sell_pct": 0.0,
                "time_of_day_histogram": {},
                "insights": [],
                "recommendations": [],
            }

        # Expose pattern analysis on the summary
        summary["pattern_analysis"] = pattern_result
        summary["fomo_buy_count"] = pattern_result.get("fomo_buy_count", 0)
        summary["panic_sell_count"] = pattern_result.get("panic_sell_count", 0)
        summary["insights"] = pattern_result.get("insights", [])
        summary["recommendations"] = pattern_result.get("recommendations", [])

        # Use the new coaching summary for UI / chat
        summary["coach_text"] = render_coaching_summary(pattern_result)

        # Add real-time AI market insights
        summary["market_context"] = self.get_realtime_insights(symbol)

        # Telegram integration: mark status and optionally push a brief alert
        summary["telegram_active"] = self.telegram.is_configured()
        if self.telegram.is_configured():
            try:
                # Lightweight notification for demo purposes
                symbol_label = symbol.upper() if symbol else "your account"
                _ = self.engine  # keep linter happy
                asyncio.run(
                    self.telegram.send_message(
                        f"📊 TradeMind AI: fresh behavioral analysis ready for {symbol_label}."
                    )
                )
            except Exception:
                # Never crash the analysis if Telegram fails
                pass

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

    def get_realtime_insights(self, symbol: str | None = None) -> dict:
        """Fetch real-time AI context using CCXT and CoinGecko logic."""
        sentiment = self.market_data.get_market_sentiment()
        global_metrics = self.market_data.get_global_market_metrics()
        symbol_info = {}
        if symbol:
            symbol_info = self.market_data.get_symbol_context(symbol)
        
        return {
            "fear_greed": sentiment,
            "global": global_metrics,
            "symbol": symbol_info
        }

    def sync_symbol(self, symbol: str, limit: int = 100, market: str = "spot", credentials: BinanceCredentials | None = None) -> int:
        client = self._build_client(market, credentials=credentials)
        trades = client.fetch_and_normalize_trades(symbol=symbol, limit=limit, market=market)
        return upsert_trades(settings.db_path, trades)

    def get_account_snapshot(self, market: str = "spot", credentials: BinanceCredentials | None = None) -> dict:
        client = self._build_client(market, credentials=credentials)
        account = client.get_account(market=market)
        if market == "spot":
            prices = client.fetch_spot_prices()
            return summarize_spot_account(account, prices=prices)
        return summarize_futures_account(account)

    def build_trader_brief(self, symbol: str | None = None, limit: int = 100, market: str = "spot", credentials: BinanceCredentials | None = None) -> str:
        summary = self.analyze_local(symbol=symbol, limit=limit)
        account = None
        try:
            account = self.get_account_snapshot(market=market, credentials=credentials)
        except Exception:
            account = None
        return render_trader_brief(summary, account=account, market=market)

    def _build_client(self, market: str, credentials: BinanceCredentials | None = None) -> BinanceClient:
        if credentials:
            return BinanceClient(credentials)

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
