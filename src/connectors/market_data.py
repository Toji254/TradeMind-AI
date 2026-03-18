from __future__ import annotations

import ccxt
import httpx
from typing import Any, Dict

class MarketDataService:
    """Service to fetch real-time market context using CCXT and external APIs."""
    
    def __init__(self):
        self.binance = ccxt.binance()
        self.coingecko_url = "https://api.coingecko.com/api/v3"

    def get_market_sentiment(self) -> Dict[str, Any]:
        """Fetch global market sentiment (e.g., Fear & Greed Index)."""
        try:
            # Fear and Greed Index is a popular open-source API
            response = httpx.get("https://api.alternative.me/fng/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "value": int(data['data'][0]['value']),
                    "classification": data['data'][0]['value_classification']
                }
        except Exception:
            pass
        return {"value": 50, "classification": "Neutral"}

    def get_symbol_context(self, symbol: str) -> Dict[str, Any]:
        """Get real-time price and volatility for a symbol using CCXT."""
        try:
            # Normalize symbol for CCXT (e.g., BTCUSDT -> BTC/USDT)
            ccxt_symbol = symbol.replace("USDT", "/USDT")
            ticker = self.binance.fetch_ticker(ccxt_symbol)
            
            return {
                "last_price": ticker['last'],
                "change_24h": ticker['percentage'],
                "high_24h": ticker['high'],
                "low_24h": ticker['low'],
                "volatility_ratio": round((ticker['high'] - ticker['low']) / ticker['low'] * 100, 2)
            }
        except Exception:
            return {}

    def get_global_market_metrics(self) -> Dict[str, Any]:
        """Fetch global market cap and volume from CoinGecko."""
        try:
            response = httpx.get(f"{self.coingecko_url}/global", timeout=10)
            if response.status_code == 200:
                data = response.json()['data']
                return {
                    "market_cap_change": data['market_cap_change_percentage_24h_usd'],
                    "btc_dominance": data['market_cap_percentage']['btc']
                }
        except Exception:
            return {}
