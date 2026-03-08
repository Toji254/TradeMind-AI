from __future__ import annotations

import sqlite3
from datetime import datetime
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


def load_trades(db_path: Path, symbol: str | None = None, limit: int = 100) -> list[TradeRecord]:
    init_db(db_path)
    query = """
        SELECT trade_id, symbol, side, price, quantity, pnl, leverage, timestamp, hour_utc, notes
        FROM trades
    """
    params: list[object] = []
    if symbol:
        query += " WHERE symbol = ?"
        params.append(symbol.upper())
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(query, params).fetchall()

    trades = [
        TradeRecord(
            trade_id=row[0],
            symbol=row[1],
            side=row[2],
            price=row[3],
            quantity=row[4],
            pnl=row[5],
            leverage=row[6],
            timestamp=datetime.fromisoformat(row[7]),
            hour_utc=row[8],
            notes=row[9],
        )
        for row in rows
    ]
    return list(reversed(trades))


def list_symbols(db_path: Path) -> list[tuple[str, int]]:
    init_db(db_path)
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT symbol, COUNT(*) as trade_count FROM trades GROUP BY symbol ORDER BY trade_count DESC, symbol ASC"
        ).fetchall()
    return [(row[0], row[1]) for row in rows]
