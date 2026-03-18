from __future__ import annotations

import logging
from src.app.services import TradeMindService
from src.app.config import settings
from src.storage.local_db import load_trades, load_journal_entries
from src.analysis.engine import AnalysisEngine
from src.coaching.interventions import build_intervention_plan

# Configure basic logging for the bridge
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trademind_bridge")

service = TradeMindService()

def handle_trademind_command(command: str) -> str:
    """
    Takes a raw text command like:
      - 'tm brief'
      - 'tm analyze BTCUSDT 50'
      - 'tm plan BTCUSDT'
      - 'tm daily'
    Runs the appropriate TradeMind logic and returns cleaned-up text.
    """
    parts = command.strip().split()
    if not parts or parts[0].lower() != "tm":
        return "Invalid command. Supported commands start with 'tm ' (e.g., 'tm brief')."

    if len(parts) < 2:
        return "Usage: tm [brief | analyze | plan | daily] [options]\nTry 'tm brief' for a quick account summary."

    action = parts[1].lower()

    try:
        if action == "brief":
            # Usage: tm brief [symbol] [market: spot/futures]
            symbol = parts[2].upper() if len(parts) > 2 else None
            market = parts[3].lower() if len(parts) > 3 else "spot"
            return service.build_trader_brief(symbol=symbol, market=market)

        elif action == "analyze":
            # Usage: tm analyze <SYMBOL> [limit] [market: spot/futures]
            if len(parts) < 3:
                return "Usage: tm analyze <SYMBOL> [limit] [market]\nExample: tm analyze BTCUSDT 50"
            
            symbol = parts[2].upper()
            limit = int(parts[3]) if len(parts) > 3 else 100
            market = parts[4].lower() if len(parts) > 4 else "spot"

            # Sync from Binance first
            logger.info(f"Syncing {limit} {market} trades for {symbol}...")
            inserted = service.sync_symbol(symbol=symbol, limit=limit, market=market)
            
            # Generate the brief/analysis
            brief = service.build_trader_brief(symbol=symbol, limit=limit, market=market)
            return f"Synced {inserted} trades for {symbol} ({market}).\n\n{brief}"

        elif action == "plan":
            # Usage: tm plan <SYMBOL> [limit]
            if len(parts) < 3:
                return "Usage: tm plan <SYMBOL> [limit]\nExample: tm plan BTCUSDT"

            symbol = parts[2].upper()
            limit = int(parts[3]) if len(parts) > 3 else 100

            # Load local trades and run analysis engine
            trades = load_trades(settings.db_path, symbol=symbol, limit=limit)
            if not trades:
                return f"No local trades found for {symbol}. Try syncing first with 'tm analyze {symbol}'."

            results = AnalysisEngine().run(trades)
            plan = build_intervention_plan(results)

            if not plan:
                return f"No active psychological guardrails suggested for {symbol} based on recent history. Keep trading with discipline!"

            response = [f"🧠 TradeMind Coaching Plan for {symbol}:"]
            for i, item in enumerate(plan, 1):
                response.append(f"{i}. {item}")
            return "\n".join(response)

        elif action == "daily":
            # Usage: tm daily [limit]
            limit = int(parts[2]) if len(parts) > 2 else 100

            trades = load_trades(settings.db_path, symbol=None, limit=limit)
            if not trades:
                return "No recent local trades found yet. Sync some history first with 'tm analyze SYMBOL'."

            results = AnalysisEngine().run(trades)
            plan = build_intervention_plan(results)

            journal_entries = load_journal_entries(settings.db_path, limit=5)

            lines: list[str] = []
            lines.append("🧠 TradeMind Daily Check-in")
            lines.append("")
            lines.append(f"Sample: {len(trades)} trades | signals: {len(results)} | guardrails: {len(plan)}")

            if plan:
                lines.append("")
                lines.append("Top guardrails for today:")
                for i, item in enumerate(plan[:5], 1):
                    lines.append(f"{i}. {item}")

            if journal_entries:
                avg_sentiment = sum(e.sentiment_compound for e in journal_entries) / len(journal_entries)
                tone: str
                if avg_sentiment < -0.25:
                    tone = "more negative / stressed"
                elif avg_sentiment > 0.25:
                    tone = "more positive / confident"
                else:
                    tone = "mostly neutral"
                lines.append("")
                lines.append(f"Recent journal tone: {avg_sentiment:+.2f} ({tone})")

            if not plan and not journal_entries:
                lines.append("")
                lines.append("No strong behavioral signals yet. Stay consistent with your current rules.")

            return "\n".join(lines)

        else:
            return f"Unknown action: {action}. Try 'brief', 'analyze', 'plan', or 'daily'."

    except Exception as e:
        logger.error(f"Error handling trademind command: {e}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    # Simple CLI test
    import sys
    if len(sys.argv) > 1:
        print(handle_trademind_command(" ".join(sys.argv[1:])))
    else:
        print(handle_trademind_command("tm brief"))
