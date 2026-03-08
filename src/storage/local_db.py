from __future__ import annotations

import sqlite3
from pathlib import Path

from src.storage.models import TradeRecord


SCHEMA = """
CREATE TABLE IF NOT EXISTS trades (
    trade_id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    side TEXT NOT NULL,
    price REAL NOT NULL,
    quantity REAL NOT NULL,
    pnl REAL NOT NULL,
    leverage REAL NOT NULL DEFAULT 1.0,
    timestamp TEXT NOT NULL,
    hour_utc INTEGER NOT NULL,
    notes TEXT
);
"""


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.executescript(SCHEMA)
        connection.commit()


def upsert_trades(db_path: Path, trades: list[TradeRecord]) -> int:
    init_db(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.executemany(
            """
            INSERT OR REPLACE INTO trades (
                trade_id, symbol, side, price, quantity, pnl, leverage, timestamp, hour_utc, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    trade.trade_id,
                    trade.symbol,
                    trade.side,
                    trade.price,
                    trade.quantity,
                    trade.pnl,
                    trade.leverage,
                    trade.timestamp.isoformat(),
                    trade.hour_utc,
                    trade.notes,
                )
                for trade in trades
            ],
        )
        connection.commit()
    return len(trades)
