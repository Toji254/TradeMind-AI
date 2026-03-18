from __future__ import annotations


def render_trader_brief(summary: dict, account: dict | None = None, market: str = "spot") -> str:
    """Render a compact, chat-friendly brief based on the analysis summary."""

    lines: list[str] = []
    
    symbol = summary.get("selected_symbol", "Account")
    discipline = summary.get("discipline_score", 50)
    
    # Header with emoji based on score
    mood_emoji = "🛡️" if discipline >= 80 else "⚠️" if discipline >= 50 else "🛑"
    lines.append(f"{mood_emoji} *TradeMind Brief: {symbol}*")
    lines.append(f"Discipline Score: *{discipline}/100*")
    lines.append("")

    # Account context
    if account:
        if market == "futures":
            val = account.get('wallet_balance', 0)
            pnl = account.get('unrealized_profit', 0)
            lines.append(f"💰 Wallet: {val:.2f} USDT | PnL: {pnl:.2f}")
        else:
            val = account.get('estimated_total_usdt', 0)
            lines.append(f"💰 Est. Value: {val:.2f} USDT")
        lines.append("")

    # Patterns
    patterns = summary.get("patterns", [])
    if patterns:
        lines.append("*Detected Patterns:*")
        for p in patterns[:3]:
            msg = p.get("message") or p.get("summary", "")
            lines.append(f"• {msg}")
        lines.append("")

    # Actions
    actions = summary.get("suggestions", [])
    if actions:
        lines.append("*Guardrail Plan:*")
        for a in actions[:3]:
            lines.append(f"✅ {a}")
    else:
        lines.append("✨ Maintaining strong discipline. No new guardrails suggested.")

    return "\n".join(lines)
