from src.connectors.binance_client import BinanceClient, BinanceCredentials


def test_normalize_spot_trade() -> None:
    client = BinanceClient(BinanceCredentials(api_key="x", api_secret="y", base_url="https://testnet.binance.vision"))
    normalized = client._normalize_spot_trade(
        {
            "id": 1,
            "symbol": "BTCUSDT",
            "isBuyer": True,
            "price": "50000",
            "qty": "0.01",
            "quoteQty": "500",
            "commission": "0.1",
            "time": 1700000000000,
        }
    )
    assert normalized.symbol == "BTCUSDT"
    assert normalized.side == "BUY"
    assert normalized.trade_id == "1"
