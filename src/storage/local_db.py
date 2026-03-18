from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from src.journal.models import JournalEntry
from src.journal.sentiment import score_text
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

CREATE TABLE IF NOT EXISTS journal_entries (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    tag TEXT NOT NULL,
    text TEXT NOT NULL,
    sentiment_compound REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_trades_symbol_time ON trades (symbol, timestamp);
CREATE INDEX IF NOT EXISTS idx_trades_time ON trades (timestamp);
CREATE INDEX IF NOT EXISTS idx_journal_time ON journal_entries (created_at);
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


def list_symbols_by_market(db_path: Path, market: str = "spot") -> list[str]:
    init_db(db_path)
    pattern = "spot_testnet%" if market == "spot" else "futures_testnet%"
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT DISTINCT symbol FROM trades WHERE notes LIKE ? ORDER BY symbol ASC",
            (pattern,),
        ).fetchall()
    return [row[0] for row in rows]


def list_symbols(db_path: Path) -> list[tuple[str, int]]:
    init_db(db_path)
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(
            "SELECT symbol, COUNT(*) as trade_count FROM trades GROUP BY symbol ORDER BY trade_count DESC, symbol ASC"
        ).fetchall()
    return [(row[0], row[1]) for row in rows]


def add_journal_entry(db_path: Path, tag: str, text: str) -> int:
    init_db(db_path)
    sentiment = score_text(text).get("compound", 0.0)
    created_at = datetime.now().astimezone().isoformat()
    with sqlite3.connect(db_path) as connection:
        cursor = connection.execute(
            "INSERT INTO journal_entries (created_at, tag, text, sentiment_compound) VALUES (?, ?, ?, ?)",
            (created_at, tag, text, sentiment),
        )
        connection.commit()
        return int(cursor.lastrowid)


def load_journal_entries(db_path: Path, limit: int = 20, tag: str | None = None) -> list[JournalEntry]:
    init_db(db_path)
    query = "SELECT entry_id, created_at, tag, text, sentiment_compound FROM journal_entries"
    params: list[object] = []
    if tag:
        query += " WHERE tag = ?"
        params.append(tag)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    with sqlite3.connect(db_path) as connection:
        rows = connection.execute(query, params).fetchall()
    return [
        JournalEntry(
            entry_id=row[0],
            created_at=datetime.fromisoformat(row[1]),
            tag=row[2],
            text=row[3],
            sentiment_compound=row[4],
        )
        for row in rows
    ]
