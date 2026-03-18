from __future__ import annotations

from src.analysis.base import DetectionResult
from src.storage.models import TradeRecord


class FomoBuyDetector:
    name = "fomo_buy"

    def detect(self, trades: list[TradeRecord]) -> DetectionResult | None:
        buys = [trade for trade in trades if trade.side.upper() == "BUY"]
        if len(buys) < 3:
            return None

        # Detect rapid clusters of buys (e.g., 3+ buys in 30 minutes)
        rapid_clusters = 0
        cluster_trade_ids = []
        for i in range(len(buys) - 2):
            t1, t3 = buys[i], buys[i+2]
            diff = (t3.timestamp - t1.timestamp).total_seconds() / 60
            if diff <= 30:
                rapid_clusters += 1
                cluster_trade_ids.extend([buys[i].trade_id, buys[i+1].trade_id, buys[i+2].trade_id])

        # Also check if they were chasing losses (original logic improved)
        chased = [trade for trade in buys if trade.pnl < 0 and (trade.leverage >= 2.0 or rapid_clusters > 0)]
        
        if rapid_clusters == 0 and len(chased) < 3:
            return None

        unique_ids = list(set(cluster_trade_ids + [t.trade_id for t in chased]))
        
        return DetectionResult(
            detector=self.name,
            pattern="FOMO / Impulse buying",
            confidence=min(0.95, 0.5 + (rapid_clusters * 0.15)),
            summary=f"Detected {rapid_clusters} instances of rapid-fire buying and impulsive entry clusters.",
            evidence={
                "buy_count": len(buys),
                "rapid_clusters": rapid_clusters,
                "impulsive_buys": len(chased)
            },
            trade_ids=unique_ids,
            coaching=[
                "Implement a 'one-candle wait' rule before chasing a breakout.",
                "If you miss the first entry, wait for a pull-back rather than market-buying the top.",
                "Limit yourself to 2 entries per 60 minutes on the same symbol."
            ],
        )
