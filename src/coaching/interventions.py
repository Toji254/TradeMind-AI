from __future__ import annotations

from src.analysis.base import DetectionResult


EXERCISES = {
    "fomo_buy": [
        "Delay entry by 10 minutes after a breakout candle.",
        "Write the exact reason this is not just green-candle chasing.",
    ],
    "panic_sell": [
        "State the invalidation level before clicking sell.",
        "Take three slow breaths before any emergency exit.",
    ],
    "revenge_trading": [
        "After two losses, step away for 15 minutes.",
        "Reduce the next trade to minimum size instead of trying to win it back.",
    ],
    "streak_behavior": [
        "Freeze size after a streak and review your last two decisions.",
        "If emotion is high, journal before the next trade.",
    ],
    "time_of_day_bias": [
        "Mark your weak trading window as high-friction time.",
        "Use a checklist instead of discretionary entries during that hour.",
    ],
    "overtrading": [
        "Add a mandatory pause timer between orders.",
        "Do not place the next trade until you can explain the setup clearly.",
    ],
}


def build_intervention_plan(results: list[DetectionResult]) -> list[str]:
    """Build a concise, de-duplicated intervention plan.

    - Prioritises detectors with higher confidence.
    - Prefers detector-specific coaching attached to the DetectionResult.
    - Falls back to EXERCISES table for any remaining guardrails.
    - De-duplicates identical lines across detectors.
    """

    plan: list[str] = []
    seen: set[str] = set()

    # Sort by confidence so the most certain signals surface first
    ordered = sorted(results, key=lambda r: getattr(r, "confidence", 0), reverse=True)

    for result in ordered:
        # 1) Use any coaching lines attached to the detection itself
        for item in getattr(result, "coaching", []) or []:
            if item not in seen:
                seen.add(item)
                plan.append(item)

        # 2) Fill in from the generic EXERCISES table for this detector
        for item in EXERCISES.get(result.detector, []):
            if item not in seen:
                seen.add(item)
                plan.append(item)

    return plan
