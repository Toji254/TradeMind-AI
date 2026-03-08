# TradeMind AI

TradeMind AI is an open-source, privacy-first OpenClaw assistant that acts like a confidential trading psychologist.

Instead of promising market predictions, it analyzes your personal trading behavior locally to uncover patterns like FOMO buying, panic selling, revenge trading, over-sizing after losses, and time-based impulsive decision making.

It then turns those findings into:

- tailored coaching sessions
- personalized mindset exercises
- behavioral strategy tweaks
- real-time intervention suggestions
- better long-term discipline

## Core Principles

- **Privacy first** — your data stays on your device by default
- **Behavior over hype** — this is about psychology and discipline, not fake alpha
- **Explainability** — rules and insights should be understandable
- **Open source** — pattern detectors and workflows are transparent
- **Local processing** — no cloud analytics required for the core product

## MVP Scope

The first version focuses on:

1. importing Binance trade history locally
2. storing it in a local SQLite database
3. detecting behavioral patterns with explainable detectors
4. generating plain-language coaching summaries
5. supporting future OpenClaw conversational workflows

## Planned Capabilities

- Binance trade sync
- behavioral pattern detection
- journaling and sentiment tagging
- coaching summaries
- anti-impulse rule suggestions
- progress tracking and weekly reviews

## Example Questions TradeMind AI Should Answer

- "Analyze my last 20 trades"
- "What emotional patterns am I repeating?"
- "Do I over-size after losses?"
- "What time of day do I trade the worst?"
- "Help me build a rule to stop revenge trading"

## Architecture Overview

- `src/app/` — CLI and config
- `src/connectors/` — exchange and market data integrations
- `src/storage/` — SQLite models and persistence
- `src/analysis/` — behavior detectors and profiling
- `src/coaching/` — insight translation and interventions
- `src/journal/` — journaling and sentiment helpers
- `src/rules/` — user-defined guardrails
- `src/reports/` — summaries and dashboard-ready output
- `tests/` — automated tests

## Quick Start

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python -m src.app.cli doctor
```

## Safety / Positioning

TradeMind AI is **not** a financial advisor and does **not** provide guaranteed returns, trade signals, or profit promises.

Its purpose is to help traders improve discipline, self-awareness, and risk behavior.

## Status

This repository is now under active MVP development.
