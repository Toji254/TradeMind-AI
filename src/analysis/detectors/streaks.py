from __future__ import annotations

from src.analysis.base import DetectionResult
from src.storage.models import TradeRecord


class StreakBehaviorDetector:
    name = "streak_behavior"

    def detect(self, trades: list[TradeRecord]) -> DetectionResult | None:
        if len(trades) < 5:
            return None

        ordered = sorted(trades, key=lambda trade: trade.timestamp)
        increased_after_losses = 0
        for index in range(2, len(ordered)):
            prev_a = ordered[index - 2]
            prev_b = ordered[index - 1]
            current = ordered[index]
            if prev_a.pnl < 0 and prev_b.pnl < 0 and current.quantity > prev_b.quantity:
                increased_after_losses += 1

        if increased_after_losses == 0:
            return None

        return DetectionResult(
            detector=self.name,
            pattern="Risk increase after losing streaks",
            confidence=min(0.9, 0.58 + increased_after_losses * 0.08),
            summary="Sizing appears to increase after consecutive losses, suggesting recent outcomes may be driving risk decisions.",
            evidence={"increased_after_losses": increased_after_losses},
            trade_ids=[trade.trade_id for trade in ordered],
            coaching=[
                "Lock size to a fixed maximum after a losing streak.",
                "Review your last two trades before changing exposure.",
            ],
        )
