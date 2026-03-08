from datetime import UTC, datetime

from src.app.services import TradeMindService
from src.storage.models import TradeRecord


def test_chart_data_shapes() -> None:
    service = TradeMindService()
    trades = [
        TradeRecord('1', 'BTCUSDT', 'BUY', 100.0, 1.0, -1.0, 1.0, datetime.now(UTC), 2, None),
        TradeRecord('2', 'BTCUSDT', 'SELL', 99.0, 1.0, 2.0, 1.0, datetime.now(UTC), 3, None),
    ]
    charts = service._build_chart_data(trades)
    assert len(charts['equity_curve']) == 2
    assert len(charts['hourly_activity']) == 24
    assert any(item['label'] == 'BUY' for item in charts['side_mix'])
