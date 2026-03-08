from __future__ import annotations

from src.analysis.base import DetectionResult
from src.coaching.interventions import build_intervention_plan
from src.journal.models import JournalEntry
from src.reports.progress import behavioral_score
from src.storage.models import TradeRecord


class Coach:
    def summarize(self, trades: list[TradeRecord], results: list[DetectionResult], journal_entries: list[JournalEntry] | None = None) -> str:
        if not trades:
            return "No local trades were found for analysis yet. Sync a symbol first, then analyze it."

        journal_entries = journal_entries or []
        score = behavioral_score(trades, results)
        lines = [
            f"Analyzed {len(trades)} trades across {len({trade.symbol for trade in trades})} symbol(s).",
            f"Buys: {sum(1 for trade in trades if trade.side.upper() == 'BUY')} | Sells: {sum(1 for trade in trades if trade.side.upper() == 'SELL')}",
            f"Proxy PnL/fee impact: {sum(trade.pnl for trade in trades):.4f}",
            f"Behavioral discipline score: {score}/100",
        ]

        if journal_entries:
            avg_sentiment = sum(entry.sentiment_compound for entry in journal_entries) / len(journal_entries)
            lines.append(f"Recent journal entries: {len(journal_entries)} | Average sentiment: {avg_sentiment:.2f}")

        if not results:
            lines.append("No strong behavioral patterns were detected in this sample.")
            return "\n".join(lines)

        lines.append("Detected behavioral signals:")
        for result in results:
            lines.append(f"- {result.pattern} ({result.confidence:.0%}): {result.summary}")
            for suggestion in result.coaching:
                lines.append(f"  • {suggestion}")

        plan = build_intervention_plan(results)
        if plan:
            lines.append("Suggested mindset / guardrail plan:")
            for item in plan:
                lines.append(f"  • {item}")
        return "\n".join(lines)
