from __future__ import annotations

from src.analysis.base import DetectionResult


class Coach:
    def summarize(self, results: list[DetectionResult]) -> str:
        if not results:
            return "No strong behavioral patterns were detected in the selected sample."

        lines = ["TradeMind AI detected these behavioral signals:"]
        for result in results:
            lines.append(f"- {result.pattern}: {result.summary}")
        return "\n".join(lines)
