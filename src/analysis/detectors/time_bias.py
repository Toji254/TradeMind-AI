from __future__ import annotations

from collections import Counter

from src.analysis.base import DetectionResult
from src.storage.models import TradeRecord


class TimeOfDayBiasDetector:
    name = "time_of_day_bias"

    def detect(self, trades: list[TradeRecord]) -> DetectionResult | None:
        losing_hours = [trade.hour_utc for trade in trades if trade.pnl < 0]
        if len(losing_hours) < 3:
            return None

        hour, count = Counter(losing_hours).most_common(1)[0]
        ratio = count / len(losing_hours)
        if ratio < 0.4:
            return None

        return DetectionResult(
            detector=self.name,
            pattern="Time-of-day loss concentration",
            confidence=min(0.9, 0.5 + ratio / 2),
            summary=f"A disproportionate share of losing trades is clustering around {hour:02d}:00 UTC.",
            evidence={"hour_utc": hour, "loss_count_at_hour": count, "total_losing_trades": len(losing_hours)},
            trade_ids=[trade.trade_id for trade in trades if trade.hour_utc == hour and trade.pnl < 0],
            coaching=[
                f"Treat trades around {hour:02d}:00 UTC as higher risk until your stats improve.",
                "Add a pre-trade self-check during your weakest trading window.",
            ],
        )
