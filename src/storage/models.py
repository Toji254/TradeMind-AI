from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TradeRecord:
    trade_id: str
    symbol: str
    side: str
    price: float
    quantity: float
    pnl: float
    leverage: float = 1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    hour_utc: int = 0
    notes: str | None = None
