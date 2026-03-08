from __future__ import annotations

from src.analysis.base import DetectionResult


def render_summary(results: list[DetectionResult]) -> dict:
    return {
        "pattern_count": len(results),
        "patterns": [
            {
                "detector": result.detector,
                "pattern": result.pattern,
                "confidence": result.confidence,
                "summary": result.summary,
                "evidence": result.evidence,
                "trade_ids": result.trade_ids,
                "coaching": result.coaching,
            }
            for result in results
        ],
    }
