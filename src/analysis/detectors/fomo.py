from __future__ import annotations

from src.analysis.base import DetectionResult
from src.storage.models import TradeRecord


class FomoBuyDetector:
    name = "fomo_buy"

    def detect(self, trades: list[TradeRecord]) -> DetectionResult | None:
        buys = [trade for trade in trades if trade.side.upper() == "BUY"]
        if len(buys) < 3:
            return None

        chased = [trade for trade in buys if trade.pnl < 0 and trade.leverage >= 2.0]
        ratio = len(chased) / len(buys)
        if ratio < 0.6:
            return None

        return DetectionResult(
            detector=self.name,
            pattern="FOMO buying tendency",
            confidence=min(0.95, 0.55 + ratio / 2),
            summary="A large share of recent buy entries were high-conviction chase attempts that still ended negative.",
            evidence={"buy_count": len(buys), "negative_high_leverage_buys": len(chased), "ratio": round(ratio, 2)},
            trade_ids=[trade.trade_id for trade in chased],
            coaching=[
                "Add a 10-15 minute delay before entering after rapid upside candles.",
                "Use smaller size on momentum entries until your chase-loss rate improves.",
            ],
        )
