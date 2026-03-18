from __future__ import annotations

from src.analysis.base import DetectionResult
from src.coaching.interventions import build_intervention_plan
from src.reports.progress import behavioral_score
from src.storage.models import TradeRecord


def render_summary(results: list[DetectionResult], trades: list[TradeRecord]) -> dict:
    total_pnl = sum(trade.pnl for trade in trades)
    buy_count = sum(1 for trade in trades if trade.side.upper() == "BUY")
    sell_count = sum(1 for trade in trades if trade.side.upper() == "SELL")
    symbols = sorted({trade.symbol for trade in trades})
    
    wins = [t for t in trades if t.pnl > 0]
    losses = [t for t in trades if t.pnl < 0]
    win_rate = (len(wins) / len(trades) * 100) if trades else 0
    
    gross_profits = sum(t.pnl for t in wins)
    gross_losses = abs(sum(t.pnl for t in losses))
    profit_factor = (gross_profits / gross_losses) if gross_losses > 0 else (gross_profits if gross_profits > 0 else 0)
    
    last_trade = trades[-1] if trades else None
    last_trade_time = last_trade.timestamp.isoformat(timespec="seconds") if last_trade else None

    return {
        "total_trades": len(trades),
        "buy_count": buy_count,
        "sell_count": sell_count,
        "total_pnl": round(total_pnl, 4),
        "win_rate": round(win_rate, 2),
        "profit_factor": round(profit_factor, 2),
        "last_trade_time": last_trade_time,
        "symbols": symbols,
        "discipline_score": behavioral_score(trades, results),
        "suggestions": build_intervention_plan(results),
        "patterns": [
            {
                "message": result.summary,
                "detector": result.detector,
            }
            for result in results
        ],
    }
