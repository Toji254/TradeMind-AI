from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class TradeRecord:
    trade_id: str
    symbol: str
    side: str
    price: float
    quantity: float
    pnl: float
    leverage: float = 1.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    hour_utc: int = 0
    notes: str | None = None

    @property
    def is_loss(self) -> bool:
        return self.pnl < 0

    @property
    def is_win(self) -> bool:
        return self.pnl > 0
