from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from urllib.parse import urlencode

import requests

from src.storage.models import TradeRecord


@dataclass
class BinanceCredentials:
    api_key: str
    api_secret: str
    base_url: str


class BinanceClient:
    """Minimal signed Binance client for spot/futures testnet account and trade sync."""

    def __init__(self, credentials: BinanceCredentials) -> None:
        self.credentials = credentials
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": credentials.api_key})

    def ping(self, market: str = "spot") -> bool:
        path = "/api/v3/ping" if market == "spot" else "/fapi/v1/ping"
        response = self.session.get(f"{self.credentials.base_url}{path}", timeout=20)
        response.raise_for_status()
        return True

    def get_account(self, market: str = "spot") -> dict:
        path = "/api/v3/account" if market == "spot" else "/fapi/v2/account"
        return self._signed_get(path)

    def fetch_spot_prices(self) -> dict[str, float]:
        response = self.session.get(f"{self.credentials.base_url}/api/v3/ticker/price", timeout=30)
        response.raise_for_status()
        rows = response.json()
        return {row["symbol"]: float(row["price"]) for row in rows}

    def fetch_my_trades(self, symbol: str, limit: int = 50) -> list[dict]:
        return self._signed_get("/api/v3/myTrades", {"symbol": symbol.upper(), "limit": limit})

    def fetch_futures_account_trades(self, symbol: str, limit: int = 50) -> list[dict]:
        return self._signed_get("/fapi/v1/userTrades", {"symbol": symbol.upper(), "limit": limit})

    def fetch_and_normalize_trades(self, symbol: str, limit: int = 50, market: str = "spot") -> list[TradeRecord]:
        if market == "spot":
            raw_trades = self.fetch_my_trades(symbol=symbol, limit=limit)
            return [self._normalize_spot_trade(trade) for trade in raw_trades]
        if market == "futures":
            raw_trades = self.fetch_futures_account_trades(symbol=symbol, limit=limit)
            return [self._normalize_futures_trade(trade) for trade in raw_trades]
        raise ValueError("market must be 'spot' or 'futures'")

    def _signed_get(self, path: str, params: dict | None = None) -> dict | list:
        query: dict[str, str | int] = dict(params or {})
        query["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(query)
        signature = hmac.new(
            self.credentials.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        url = f"{self.credentials.base_url}{path}?{query_string}&signature={signature}"
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return response.json()

    def _normalize_spot_trade(self, trade: dict) -> TradeRecord:
        trade_time = datetime.fromtimestamp(trade["time"] / 1000, tz=UTC)
        qty = Decimal(str(trade["qty"]))
        price = Decimal(str(trade["price"]))
        quote_qty = Decimal(str(trade.get("quoteQty", "0")))
        gross_value = quote_qty if quote_qty else qty * price
        fee = Decimal(str(trade.get("commission", "0")))
        realized_proxy = float(-fee)

        return TradeRecord(
            trade_id=str(trade["id"]),
            symbol=trade["symbol"],
            side="BUY" if trade.get("isBuyer") else "SELL",
            price=float(price),
            quantity=float(qty),
            pnl=realized_proxy,
            leverage=1.0,
            timestamp=trade_time,
            hour_utc=trade_time.hour,
            notes=f"spot_testnet gross_value={gross_value}",
        )

    def _normalize_futures_trade(self, trade: dict) -> TradeRecord:
        trade_time = datetime.fromtimestamp(trade["time"] / 1000, tz=UTC)
        qty = Decimal(str(trade.get("qty") or trade.get("origQty") or "0"))
        price = Decimal(str(trade.get("price", "0")))
        realized_pnl = Decimal(str(trade.get("realizedPnl", "0")))
        commission = Decimal(str(trade.get("commission", "0")))
        leverage_proxy = Decimal("1")

        return TradeRecord(
            trade_id=f"futures-{trade['id']}",
            symbol=trade["symbol"],
            side=str(trade.get("side", "BUY")).upper(),
            price=float(price),
            quantity=float(abs(qty)),
            pnl=float(realized_pnl - commission),
            leverage=float(leverage_proxy),
            timestamp=trade_time,
            hour_utc=trade_time.hour,
            notes="futures_testnet",
        )
