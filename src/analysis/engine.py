from __future__ import annotations

from src.analysis.base import DetectionResult
from src.analysis.detectors.fomo import FomoBuyDetector
from src.analysis.detectors.overtrading import OvertradingDetector
from src.analysis.detectors.panic_sell import PanicSellDetector
from src.analysis.detectors.revenge import RevengeTradingDetector
from src.analysis.detectors.streaks import StreakBehaviorDetector
from src.analysis.detectors.time_bias import TimeOfDayBiasDetector
from src.storage.models import TradeRecord


class AnalysisEngine:
    def __init__(self) -> None:
        self.detectors = [
            FomoBuyDetector(),
            PanicSellDetector(),
            RevengeTradingDetector(),
            StreakBehaviorDetector(),
            TimeOfDayBiasDetector(),
            OvertradingDetector(),
        ]

    def run(self, trades: list[TradeRecord]) -> list[DetectionResult]:
        results: list[DetectionResult] = []
        for detector in self.detectors:
            result = detector.detect(trades)
            if result is not None:
                results.append(result)
        return results
