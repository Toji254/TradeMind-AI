from src.reports.account import summarize_futures_account, summarize_spot_account
from src.reports.messaging import render_trader_brief


def test_summarize_spot_account() -> None:
    summary = summarize_spot_account(
        {
            'balances': [
                {'asset': 'USDT', 'free': '100', 'locked': '0'},
                {'asset': 'BTC', 'free': '0.5', 'locked': '0'},
            ]
        },
        prices={'BTCUSDT': 60000},
    )
    assert summary['asset_count'] == 2
    assert summary['estimated_total_usdt'] == 30100.0


def test_summarize_futures_account() -> None:
    summary = summarize_futures_account(
        {
            'totalWalletBalance': '250',
            'totalUnrealizedProfit': '-12.5',
            'availableBalance': '180',
            'assets': [{'asset': 'USDT'}],
            'positions': [{'symbol': 'BTCUSDT', 'positionAmt': '0.01'}],
        }
    )
    assert summary['wallet_balance'] == 250.0
    assert summary['position_count'] == 1


def test_render_trader_brief() -> None:
    text = render_trader_brief(
        {
            'trade_count': 6,
            'pattern_count': 1,
            'behavioral_score': 88,
            'total_pnl': -1.2,
            'patterns': [{'pattern': 'Rapid-fire trading cluster', 'confidence': 0.72, 'summary': 'Trading too fast.'}],
            'intervention_plan': ['Pause between trades.'],
        },
        account={'estimated_total_usdt': 1200.0, 'asset_count': 3},
        market='spot',
    )
    assert 'Spot account est.' in text
    assert 'Rapid-fire trading cluster' in text
