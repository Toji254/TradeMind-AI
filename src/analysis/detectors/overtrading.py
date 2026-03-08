from __future__ import annotations

from src.analysis.base import DetectionResult
from src.storage.models import TradeRecord


class OvertradingDetector:
    name = "overtrading"

    def detect(self, trades: list[TradeRecord]) -> DetectionResult | None:
        if len(trades) < 6:
            return None

        ordered = sorted(trades, key=lambda trade: trade.timestamp)
        intervals = [
            (ordered[index].timestamp - ordered[index - 1].timestamp).total_seconds()
            for index in range(1, len(ordered))
        ]
        if not intervals:
            return None

        avg_interval = sum(intervals) / len(intervals)
        if avg_interval > 180:
            return None

        return DetectionResult(
            detector=self.name,
            pattern="Rapid-fire trading cluster",
            confidence=0.72,
            summary="Trades are arriving in a very tight sequence, which can signal impulsive clicking rather than deliberate execution.",
            evidence={"avg_seconds_between_trades": round(avg_interval, 1), "trade_count": len(trades)},
            trade_ids=[trade.trade_id for trade in ordered],
            coaching=[
                "Add a mandatory pause between entries during active sessions.",
                "Write down the reason for each trade before submitting the next one.",
            ],
        )
