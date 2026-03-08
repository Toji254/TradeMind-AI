from pathlib import Path
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from src.app.config import settings
from src.storage.local_db import init_db, upsert_trades
from src.storage.models import TradeRecord
from src.web.app import app


def test_dashboard_renders_with_local_data(tmp_path: Path) -> None:
    original_db = settings.db_path
    settings.db_path = tmp_path / 'trademind.db'
    try:
        init_db(settings.db_path)
        upsert_trades(
            settings.db_path,
            [
                TradeRecord('1', 'BTCUSDT', 'BUY', 100.0, 1.0, -1.0, 1.0, datetime.now(UTC), 2, None),
                TradeRecord('2', 'BTCUSDT', 'SELL', 99.0, 1.0, -1.0, 1.0, datetime.now(UTC), 2, None),
            ],
        )
        client = TestClient(app)
        response = client.get('/')
        assert response.status_code == 200
        assert 'TradeMind AI' in response.text
        assert 'Behavioral score' in response.text
    finally:
        settings.db_path = original_db
