from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TradingRule:
    name: str
    description: str


class RuleEngine:
    def suggested_rules(self) -> list[TradingRule]:
        return [
            TradingRule("cooldown_after_two_losses", "Pause for 15 minutes after two consecutive losses."),
            TradingRule("cap_size_after_drawdown", "Do not increase position size while in a loss streak."),
        ]
