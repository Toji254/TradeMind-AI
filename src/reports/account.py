from __future__ import annotations

from decimal import Decimal


def summarize_spot_account(account: dict, prices: dict[str, float] | None = None) -> dict:
    prices = prices or {}
    balances = account.get("balances", [])
    non_zero = []
    estimated_total_usdt = Decimal("0")

    for balance in balances:
        free = Decimal(str(balance.get("free", 0)))
        locked = Decimal(str(balance.get("locked", 0)))
        total = free + locked
        if total == 0:
            continue
        asset = balance.get("asset", "")
        non_zero.append({"asset": asset, "total": float(total)})
        if asset == "USDT":
            estimated_total_usdt += total
        else:
            estimated_total_usdt += total * Decimal(str(prices.get(f"{asset}USDT", 0)))

    top_assets = sorted(non_zero, key=lambda item: item["total"], reverse=True)[:8]
    return {
        "asset_count": len(non_zero),
        "estimated_total_usdt": float(round(estimated_total_usdt, 2)),
        "top_assets": top_assets,
    }


def summarize_futures_account(account: dict) -> dict:
    return {
        "wallet_balance": float(account.get("totalWalletBalance", 0)),
        "unrealized_profit": float(account.get("totalUnrealizedProfit", 0)),
        "available_balance": float(account.get("availableBalance", 0)),
        "asset_count": len(account.get("assets", [])),
        "position_count": len([p for p in account.get("positions", []) if float(p.get("positionAmt", 0)) != 0]),
    }
