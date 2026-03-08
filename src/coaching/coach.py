from __future__ import annotations

from src.analysis.base import DetectionResult
from src.storage.models import TradeRecord


class Coach:
    def summarize(self, trades: list[TradeRecord], results: list[DetectionResult]) -> str:
        if not trades:
            return "No local trades were found for analysis yet. Sync a symbol first, then analyze it."

        lines = [
            f"Analyzed {len(trades)} trades across {len({trade.symbol for trade in trades})} symbol(s).",
            f"Buys: {sum(1 for trade in trades if trade.side.upper() == 'BUY')} | Sells: {sum(1 for trade in trades if trade.side.upper() == 'SELL')}",
            f"Proxy PnL/fee impact: {sum(trade.pnl for trade in trades):.4f}",
        ]

        if not results:
            lines.append("No strong behavioral patterns were detected in this sample.")
            return "\n".join(lines)

        lines.append("Detected behavioral signals:")
        for result in results:
            lines.append(f"- {result.pattern} ({result.confidence:.0%}): {result.summary}")
            for suggestion in result.coaching:
                lines.append(f"  • {suggestion}")
        return "\n".join(lines)
