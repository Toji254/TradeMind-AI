from __future__ import annotations

from src.analysis.base import DetectionResult
from src.storage.models import TradeRecord


class PanicSellDetector:
    name = "panic_sell"

    def detect(self, trades: list[TradeRecord]) -> DetectionResult | None:
        sells = [trade for trade in trades if trade.side.upper() == "SELL"]
        if len(sells) < 3:
            return None

        weak_sells = [trade for trade in sells if trade.pnl < 0]
        ratio = len(weak_sells) / len(sells)
        if ratio < 0.6:
            return None

        return DetectionResult(
            detector=self.name,
            pattern="Panic selling tendency",
            confidence=min(0.92, 0.55 + ratio / 2),
            summary="A large share of recent sell decisions locked in immediate negative outcomes, suggesting exits may be driven by fear more than process.",
            evidence={"sell_count": len(sells), "negative_sells": len(weak_sells), "ratio": round(ratio, 2)},
            trade_ids=[trade.trade_id for trade in weak_sells],
            coaching=[
                "Before selling, write the invalidation reason in one sentence.",
                "If a sell is fear-driven, wait one minute and re-check whether your original trade thesis actually broke.",
            ],
        )
