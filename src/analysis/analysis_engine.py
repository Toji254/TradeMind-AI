"""
TradeMind AI - Core Analysis Engine
A production-ready module for behavioral trading psychology analysis.
Built for local-first analysis of Binance trade history.
"""

import argparse
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# --- OPENCLAW INTEGRATION HINTS ---
# This module can be wrapped by an OpenClaw AgentSkill by defining a command like:
# tm analyze [symbol] [limit]
#
# Implementation Strategy:
# 1. Skill Logic:
#    - Use a database connector (e.g., SQLite) to fetch the last N trade records for the symbol.
#    - Convert records to a list of dicts: [{'price': p, 'time': t, 'isBuyer': b}, ...]
#    - Call result = analyze_patterns(trades)
#    - Call summary = render_coaching_summary(result)
#    - Return summary as the agent's primary text response.
# 2. Workflow:
#    - Step A: [Binance Fetch Trades] -> provides raw list.
#    - Step B: [Analysis Engine] -> this module processes the list.
#    - Step C: [Coach Message] -> uses the 'summary' to reply to the user via Telegram/WhatsApp.
# ----------------------------------

def analyze_patterns(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyzes a list of trades for behavioral patterns like FOMO buys and panic sells.
    
    Args:
        trades: List of trade dictionaries with 'price', 'time', and 'isBuyer'.
        
    Returns:
        A dictionary containing counts, percentages, insights, and recommendations.
    """
    # 1. Handle empty input
    if not trades:
        return {
            "total_trades": 0,
            "fomo_buy_count": 0,
            "fomo_buy_pct": 0.0,
            "panic_sell_count": 0,
            "panic_sell_pct": 0.0,
            "time_of_day_histogram": {},
            "insights": ["No trades found to analyze."],
            "recommendations": ["Start trading or sync your history to get behavioral coaching."]
        }

    # 2. Convert to DataFrame and sanitize
    df = pd.DataFrame(trades)
    
    # Ensure required columns exist
    required_cols = {'price', 'time', 'isBuyer'}
    if not required_cols.issubset(df.columns):
        logger.error(f"Missing required columns. Found: {df.columns}")
        return {"error": "Malformed input: missing price, time, or isBuyer fields."}

    # Drop malformed rows (skip rows where price or time conversion fails)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['time'] = pd.to_datetime(df['time'], errors='coerce', unit='ms' if isinstance(trades[0].get('time'), (int, float)) else None)
    df['isBuyer'] = df['isBuyer'].map({True: True, False: False, 'True': True, 'False': False, 1: True, 0: False})
    
    df = df.dropna(subset=['price', 'time', 'isBuyer']).sort_values('time')
    
    total_trades = len(df)
    if total_trades == 0:
        return analyze_patterns([]) # Recurse to empty handler

    # 3. Behavioral Logic: MA10 and Thresholds
    # Calculate 10-period SMA
    df['ma10'] = df['price'].rolling(window=10).mean()
    
    # Detect patterns
    # Note: If < 10 trades, ma10 will be NaN for those rows, effectively skipping detection
    fomo_mask = (df['isBuyer'] == True) & (df['price'] > 1.02 * df['ma10'])
    panic_mask = (df['isBuyer'] == False) & (df['price'] < 0.98 * df['ma10'])
    
    fomo_buy_count = int(fomo_mask.sum())
    panic_sell_count = int(panic_mask.sum())
    
    # Calculate percentages based on respective sides (buys for FOMO, sells for Panic)
    buys = df[df['isBuyer'] == True]
    sells = df[df['isBuyer'] == False]
    
    fomo_buy_pct = (fomo_buy_count / len(buys) * 100) if len(buys) > 0 else 0.0
    panic_sell_pct = (panic_sell_count / len(sells) * 100) if len(sells) > 0 else 0.0

    # 4. Time of Day Histogram
    df['hour'] = df['time'].dt.hour
    hour_counts = df['hour'].value_counts().sort_index().to_dict()
    time_of_day_histogram = {int(k): int(v) for k, v in hour_counts.items()}

    # 5. Generate Insights and Recommendations
    insights = []
    recommendations = []
    
    # Dynamic Insights
    insights.append(f"Analyzed {total_trades} total trades.")
    if fomo_buy_count > 0:
        insights.append(f"{fomo_buy_pct:.1f}% of your buys qualify as FOMO entries (2%+ above MA10).")
    if panic_sell_count > 0:
        insights.append(f"{panic_sell_pct:.1f}% of your sells look like panic exits (2%+ below MA10).")
    
    if fomo_buy_count == 0 and panic_sell_count == 0 and total_trades >= 10:
        insights.append("Your entries and exits are well-aligned with recent price averages.")

    # Rules-based Recommendations
    if fomo_buy_pct > 20:
        recommendations.append("Adopt a 'one-candle wait' rule: wait for a full period to close before entering a fast move.")
        recommendations.append("Set a strict chase cutoff: never enter more than 0.5% away from your planned level.")
    
    if panic_sell_pct > 15:
        recommendations.append("Use hard Stop Losses set at the time of entry to avoid manual panic clicks.")
        recommendations.append("Take a 15-minute cooldown away from the screen after a volatile exit.")
        
    if not recommendations:
        recommendations.append("Maintain your current discipline. Review your trading journal for edge cases.")

    return {
        "total_trades": total_trades,
        "fomo_buy_count": fomo_buy_count,
        "fomo_buy_pct": round(fomo_buy_pct, 2),
        "panic_sell_count": panic_sell_count,
        "panic_sell_pct": round(panic_sell_pct, 2),
        "time_of_day_histogram": time_of_day_histogram,
        "insights": insights,
        "recommendations": recommendations,
    }

def render_coaching_summary(result: Dict[str, Any]) -> str:
    """
    Builds a short, chat-friendly coaching summary under 800 characters.
    """
    if result.get("total_trades", 0) == 0:
        return "Discipline Check: No trade data available. Connect your Binance account to start analysis."

    fomo = result["fomo_buy_pct"]
    panic = result["panic_sell_pct"]
    
    # Determine Headline
    if fomo < 10 and panic < 10:
        headline = "Discipline Status: EXCELLENT. You are trading with high technical awareness."
    elif fomo > 25 or panic > 25:
        headline = "Discipline Status: WARNING. Emotional triggers are impacting your performance."
    else:
        headline = "Discipline Status: MIXED. There is room to tighten your execution rules."

    # Build Body
    body = [
        headline,
        f"- {result['total_trades']} trades analyzed.",
        f"- {fomo}% of buys were FOMO (chasing price).",
        f"- {panic}% of sells were PANIC (exiting lows).",
        "",
        "Guardrail Rules to Adopt:",
    ]
    
    for rec in result["recommendations"][:3]: # Keep it short
        body.append(f"  * {rec}")
        
    summary = "\n".join(body)
    return summary[:800] # Safety truncation

def main():
    parser = argparse.ArgumentParser(description="TradeMind AI Analysis CLI")
    parser.add_argument("--input", type=str, required=True, help="Path to JSON file containing trade history")
    args = parser.parse_args()

    try:
        with open(args.input, 'r') as f:
            trades = json.load(f)
            
        result = analyze_patterns(trades)
        
        # Output Metrics
        print(json.dumps(result, indent=2))
        print("\n" + "="*40 + "\n")
        
        # Output Coaching
        print(render_coaching_summary(result))
        
    except FileNotFoundError:
        print(f"Error: File '{args.input}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from '{args.input}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
