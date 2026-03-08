from pathlib import Path

from src.analysis.engine import AnalysisEngine
from src.coaching.coach import Coach
from src.storage.local_db import init_db, load_trades, upsert_trades
from src.storage.models import TradeRecord
from datetime import UTC, datetime


def test_local_analysis_pipeline_round_trip(tmp_path: Path) -> None:
    db_path = tmp_path / 'trademind.db'
    init_db(db_path)
    trades = [
        TradeRecord('1', 'BTCUSDT', 'BUY', 100.0, 1.0, -1.0, 1.0, datetime.now(UTC), 10, None),
        TradeRecord('2', 'BTCUSDT', 'SELL', 99.0, 1.0, -1.0, 1.0, datetime.now(UTC), 10, None),
        TradeRecord('3', 'BTCUSDT', 'BUY', 98.0, 2.0, -1.0, 1.0, datetime.now(UTC), 10, None),
        TradeRecord('4', 'BTCUSDT', 'SELL', 97.0, 2.0, -1.0, 1.0, datetime.now(UTC), 10, None),
        TradeRecord('5', 'BTCUSDT', 'BUY', 96.0, 2.0, -1.0, 1.0, datetime.now(UTC), 10, None),
        TradeRecord('6', 'BTCUSDT', 'SELL', 95.0, 2.0, -1.0, 1.0, datetime.now(UTC), 10, None),
    ]
    upsert_trades(db_path, trades)
    loaded = load_trades(db_path, symbol='BTCUSDT', limit=20)
    results = AnalysisEngine().run(loaded)
    summary = Coach().summarize(loaded, results)
    assert len(loaded) == 6
    assert 'Analyzed 6 trades' in summary
    assert len(results) >= 1
