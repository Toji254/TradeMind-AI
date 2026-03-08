from __future__ import annotations

from src.analysis.base import DetectionResult
from src.storage.models import TradeRecord


def render_summary(results: list[DetectionResult], trades: list[TradeRecord]) -> dict:
    total_pnl = round(sum(trade.pnl for trade in trades), 4)
    buy_count = sum(1 for trade in trades if trade.side.upper() == "BUY")
    sell_count = sum(1 for trade in trades if trade.side.upper() == "SELL")
    symbols = sorted({trade.symbol for trade in trades})

    return {
        "trade_count": len(trades),
        "buy_count": buy_count,
        "sell_count": sell_count,
        "total_pnl": total_pnl,
        "symbols": symbols,
        "pattern_count": len(results),
        "patterns": [
            {
                "detector": result.detector,
                "pattern": result.pattern,
                "confidence": result.confidence,
                "summary": result.summary,
                "evidence": result.evidence,
                "trade_ids": result.trade_ids,
                "coaching": result.coaching,
            }
            for result in results
        ],
    }
