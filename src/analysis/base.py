from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from src.storage.models import TradeRecord


@dataclass
class DetectionResult:
    detector: str
    pattern: str
    confidence: float
    summary: str
    evidence: dict[str, Any] = field(default_factory=dict)
    trade_ids: list[str] = field(default_factory=list)
    coaching: list[str] = field(default_factory=list)


class Detector(Protocol):
    name: str

    def detect(self, trades: list[TradeRecord]) -> DetectionResult | None:
        ...
