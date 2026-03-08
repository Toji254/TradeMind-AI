from pathlib import Path

from src.analysis.engine import AnalysisEngine
from src.coaching.coach import Coach
from src.storage.local_db import add_journal_entry, init_db, load_journal_entries, upsert_trades
from src.storage.models import TradeRecord
from datetime import UTC, datetime


def test_journal_entries_show_up_in_coaching_summary(tmp_path: Path) -> None:
    db_path = tmp_path / 'trademind.db'
    init_db(db_path)
    trades = [
        TradeRecord('1', 'BTCUSDT', 'BUY', 100.0, 1.0, -1.0, 1.0, datetime.now(UTC), 2, None),
        TradeRecord('2', 'BTCUSDT', 'SELL', 99.0, 1.0, -1.0, 1.0, datetime.now(UTC), 2, None),
        TradeRecord('3', 'BTCUSDT', 'BUY', 98.0, 1.0, -1.0, 1.0, datetime.now(UTC), 2, None),
        TradeRecord('4', 'BTCUSDT', 'SELL', 97.0, 1.0, -1.0, 1.0, datetime.now(UTC), 2, None),
        TradeRecord('5', 'BTCUSDT', 'BUY', 96.0, 1.0, -1.0, 1.0, datetime.now(UTC), 2, None),
        TradeRecord('6', 'BTCUSDT', 'SELL', 95.0, 1.0, -1.0, 1.0, datetime.now(UTC), 2, None),
    ]
    upsert_trades(db_path, trades)
    add_journal_entry(db_path, tag='pretrade', text='I feel anxious and want to chase the candle.')
    entries = load_journal_entries(db_path, limit=5)
    summary = Coach().summarize(trades, AnalysisEngine().run(trades), journal_entries=entries)
    assert len(entries) == 1
    assert 'Recent journal entries: 1' in summary
    assert 'Behavioral discipline score:' in summary
