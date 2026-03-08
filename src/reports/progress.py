from __future__ import annotations

from src.analysis.base import DetectionResult
from src.storage.models import TradeRecord


def behavioral_score(trades: list[TradeRecord], results: list[DetectionResult]) -> int:
    if not trades:
        return 50
    score = 100
    score -= min(40, len(results) * 12)
    negative_ratio = sum(1 for trade in trades if trade.pnl < 0) / max(1, len(trades))
    score -= int(negative_ratio * 20)
    return max(0, min(100, score))
