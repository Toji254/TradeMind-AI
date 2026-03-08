# TradeMind AI

TradeMind AI is an open-source, privacy-first OpenClaw assistant that acts like a confidential trading psychologist.

Instead of pretending to predict the market, it analyzes your personal trading behavior locally to uncover emotional patterns like FOMO buying, panic selling, revenge trading, overtrading, poor streak behavior, and time-based impulsive decision making.

It then turns those findings into:

- tailored coaching sessions
- personalized mindset exercises
- behavioral strategy tweaks
- real-time intervention suggestions
- better long-term discipline
- a local journal-backed feedback loop
- a dark-mode trading dashboard inspired by serious exchange UIs

## Core Principles

- **Privacy first** — your data stays on your device by default
- **Behavior over hype** — this is about psychology and discipline, not fake alpha
- **Explainability** — rules and insights should be understandable
- **Open source** — pattern detectors and workflows are transparent
- **Local processing** — no cloud analytics required for the core product

## Current V1 Capabilities

- Binance Spot Testnet account connectivity
- Futures-ready testnet config path and sync plumbing
- local trade sync into SQLite
- local symbol discovery
- behavior detectors for:
  - FOMO buying
  - panic selling
  - revenge trading
  - streak behavior
  - time-of-day loss concentration
  - rapid-fire overtrading
- coaching-style local analysis reports
- journal entry capture with sentiment scoring
- generated intervention / guardrail plans
- JSON analysis output for future UI or OpenClaw delivery
- OKX-inspired dark web UI with:
  - dashboard stats
  - local symbol switching
  - sync form
  - equity curve chart
  - hourly activity chart
  - side mix chart
  - patterns panel
  - guardrail plan panel
  - journal workflow

## Quick Start

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python -m src.app.cli doctor
python -m src.app.cli init
python -m src.app.cli sync-and-analyze --symbol BTCUSDT --market spot
```

## Run the Web UI

```bash
python -m src.app.cli serve-web --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

## Useful Commands

```bash
python -m src.app.cli binance-ping --market spot
python -m src.app.cli binance-account --market spot
python -m src.app.cli sync-binance --symbol BTCUSDT --limit 50 --market spot
python -m src.app.cli sync-binance --symbol BTCUSDT --limit 50 --market futures
python -m src.app.cli analyze-local --symbol BTCUSDT --limit 50
python -m src.app.cli coaching-plan --symbol BTCUSDT
python -m src.app.cli journal-add --tag pretrade "Feeling impatient after missing the move"
python -m src.app.cli journal-list
python -m src.app.cli serve-web
```

## Futures Note

Futures support is now wired in the code path, but you still need to provide:

- `BINANCE_FUTURES_API_KEY`
- `BINANCE_FUTURES_API_SECRET`

in your local `.env` before live futures testnet sync/auth can run.

## Safety / Positioning

TradeMind AI is **not** a financial advisor and does **not** provide guaranteed returns, trade signals, or profit promises.

Its purpose is to help traders improve discipline, self-awareness, and risk behavior.
