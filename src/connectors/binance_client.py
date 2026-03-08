from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BinanceCredentials:
    api_key: str
    api_secret: str


class BinanceClient:
    """Placeholder Binance client for future trade sync support."""

    def __init__(self, credentials: BinanceCredentials) -> None:
        self.credentials = credentials

    def ping(self) -> bool:
        return True

    def fetch_recent_trades(self, limit: int = 50) -> list[dict]:
        """Stub method for future implementation."""
        return []
