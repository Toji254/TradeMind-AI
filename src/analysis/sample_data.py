from __future__ import annotations

from datetime import datetime, timedelta, UTC

from src.storage.models import TradeRecord


BASE = datetime.now(UTC)


def sample_trades() -> list[TradeRecord]:
    return [
        TradeRecord("t1", "BTCUSDT", "BUY", 64000, 0.010, -12, 2.0, BASE - timedelta(hours=10), 2),
        TradeRecord("t2", "BTCUSDT", "SELL", 63500, 0.010, -18, 2.0, BASE - timedelta(hours=9, minutes=50), 2),
        TradeRecord("t3", "BTCUSDT", "BUY", 64550, 0.020, -25, 3.0, BASE - timedelta(hours=9, minutes=30), 2),
        TradeRecord("t4", "BTCUSDT", "BUY", 64880, 0.025, -10, 3.0, BASE - timedelta(hours=8, minutes=55), 3),
        TradeRecord("t5", "BTCUSDT", "SELL", 63900, 0.025, -32, 3.0, BASE - timedelta(hours=8, minutes=40), 3),
        TradeRecord("t6", "BTCUSDT", "BUY", 65220, 0.040, 5, 4.0, BASE - timedelta(hours=1), 14),
        TradeRecord("t7", "BTCUSDT", "SELL", 65190, 0.040, -14, 4.0, BASE - timedelta(minutes=50), 14),
    ]
