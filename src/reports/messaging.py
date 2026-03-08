from __future__ import annotations


def render_trader_brief(summary: dict, account: dict | None = None, market: str = "spot") -> str:
    lines: list[str] = []

    if account:
        if market == "futures":
            lines.append(f"Futures account: wallet {account.get('wallet_balance', 0):.2f} USDT | unrealized {account.get('unrealized_profit', 0):.2f} USDT | available {account.get('available_balance', 0):.2f} USDT")
        else:
            lines.append(f"Spot account est.: ~{account.get('estimated_total_usdt', 0):.2f} USDT across {account.get('asset_count', 0)} assets")

    lines.append(
        f"Analysis sample: {summary.get('trade_count', 0)} trades | patterns: {summary.get('pattern_count', 0)} | discipline score: {summary.get('behavioral_score', 50)}/100"
    )
    if summary.get("total_pnl") is not None:
        lines.append(f"Local PnL proxy: {summary.get('total_pnl', 0):.4f}")

    patterns = summary.get("patterns", [])[:3]
    if patterns:
        lines.append("Top signals:")
        for pattern in patterns:
            lines.append(f"- {pattern['pattern']} ({round(pattern['confidence'] * 100)}%): {pattern['summary']}")

    plan = summary.get("intervention_plan", [])[:3]
    if plan:
        lines.append("Suggested next actions:")
        for item in plan:
            lines.append(f"- {item}")

    if not patterns:
        lines.append("No strong behavioral issues detected in the current sample.")

    return "\n".join(lines)
