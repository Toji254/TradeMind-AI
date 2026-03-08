from __future__ import annotations

from src.analysis.base import DetectionResult
from src.storage.models import TradeRecord


class RevengeTradingDetector:
    name = "revenge_trading"

    def detect(self, trades: list[TradeRecord]) -> DetectionResult | None:
        if len(trades) < 4:
            return None

        escalations = []
        for index in range(2, len(trades)):
            prev_a = trades[index - 2]
            prev_b = trades[index - 1]
            current = trades[index]
            if prev_a.pnl < 0 and prev_b.pnl < 0 and current.quantity > max(prev_a.quantity, prev_b.quantity) * 1.5:
                escalations.append(current)

        if not escalations:
            return None

        return DetectionResult(
            detector=self.name,
            pattern="Revenge trading after losses",
            confidence=min(0.95, 0.65 + len(escalations) * 0.1),
            summary="Position size appears to jump after consecutive losses, which often signals tilt or a need to win it back fast.",
            evidence={"escalation_count": len(escalations)},
            trade_ids=[trade.trade_id for trade in escalations],
            coaching=[
                "Freeze position size after two losses in a row.",
                "Trigger a cooldown checklist before the next entry after a loss streak.",
            ],
        )
