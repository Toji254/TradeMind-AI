from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class JournalEntry:
    entry_id: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    tag: str = "general"
    text: str = ""
    sentiment_compound: float = 0.0
