# TradeMind AI

> **A privacy-first behavioral trading coach for Binance traders — built with Python, FastAPI, SQLite, explainable behavioral detectors, and an OpenClaw integration.**

<p align="center">
  <strong>Binance OpenClaw AI Assistant Build Contest — 3rd Place</strong><br/>
  <strong>Prize: 6 BNB</strong>
</p>

## Why I built this

Trading tools usually focus on price, indicators, and execution. TradeMind AI focuses on the trader.

The project analyzes a trader's own history to surface repeat behavioral patterns such as:

- FOMO buying
- panic selling
- revenge trading
- overtrading
- streak behavior
- time-of-day bias

It then turns those findings into a **behavioral discipline score, coaching summary, and practical guardrails**.

The design goal is simple: make the analysis useful without sending a trader's history to a third-party analytics service by default.

## Hackathon result

TradeMind AI was built for the **Binance OpenClaw AI Assistant Build Contest (March 4–18, 2026)**.

**Result: 3rd place — 6 BNB**

The repository includes the product, analysis pipeline, dashboard, tests, and the demo automation used to present the OpenClaw experience.

Official references:

- [Binance contest announcement](https://x.com/binance/status/2029134767917285768)
- [TradeMind AI submission](https://x.com/Mrblank254/status/2034227318768505230)
- [Binance winner announcement](https://x.com/binance/status/2041259653305114833)

## What is actually in the repo

### Behavioral analysis engine

An explainable rule-based pipeline currently includes detectors for FOMO, panic selling, revenge trading, streak behavior, time-of-day bias, and overtrading.

The project deliberately starts with interpretable rules rather than hiding the core decision-making behind an opaque model.

### Local data pipeline

Trade history is normalized into an internal model, stored in SQLite, and analyzed locally.

Current flow:

```text
Binance
  ↓
Exchange connector
  ↓
Normalized trade records
  ↓
Local SQLite
  ↓
Behavior detectors
  ↓
Behavioral profile
  ↓
Coaching / guardrails
```

### Web dashboard

A dark terminal-style dashboard provides:

- behavioral score
- trade statistics
- charts
- journal capture
- local sync and analysis
- coaching output

### CLI

The same core services are usable from the terminal:

```bash
python -m src.app.cli doctor
python -m src.app.cli init
python -m src.app.cli sync-binance --symbol BTCUSDT --limit 50 --market spot
python -m src.app.cli analyze-local --symbol BTCUSDT
python -m src.app.cli coaching-plan --symbol BTCUSDT
```

### OpenClaw + Telegram integration

TradeMind can expose generated reports to an OpenClaw-based assistant workflow and can optionally send behavioral alerts through Telegram.

The OpenClaw pieces in this repository include both integration code and presentation/demo tooling.

## Architecture

The project is split into clear layers:

| Layer | Responsibility |
| --- | --- |
| **Connectors** | Pull authorized trading data from Binance |
| **Storage** | Persist normalized trades and journal entries locally |
| **Analysis** | Detect repeat behavioral patterns |
| **Coaching** | Turn findings into interventions and guardrails |
| **Reports** | Format results for CLI, dashboard, OpenClaw, and Telegram |

See [docs/architecture.md](docs/architecture.md) for the fuller design notes.

## Security & privacy

TradeMind is designed around a local-first workflow.

- Binance credentials are provided through environment variables or the local UI rather than committed to source.
- Read-only exchange access is the recommended setup.
- The project does not execute trades or withdrawals.
- Local SQLite storage keeps the primary analysis dataset on the user's machine.

**Demo note:** the OpenClaw presentation scripts require a local `DEMO_GATEWAY_TOKEN` when the local gateway requests authentication. No gateway credential is stored in the repository.

## Getting started

### Requirements

- Python 3.14+
- Git
- Binance testnet API credentials for live testnet sync
- Optional: Playwright/Chromium for the demo automation

### Setup

```bash
git clone https://github.com/Toji254/TradeMind-AI.git
cd TradeMind-AI

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
```

Initialize the local database:

```bash
python -m src.app.cli init
```

Run the dashboard:

```bash
python -m src.app.cli serve-web
```

Then open `http://127.0.0.1:8000`.

## Tech stack

**Python · FastAPI · Typer · SQLite · SQLAlchemy · Pandas · NumPy · VaderSentiment · Chart.js · Binance APIs · Telegram Bot API · OpenClaw · Playwright**

## Project status

This repository is a documented snapshot of the TradeMind AI build and hackathon work.

The original product direction is intentionally preserved: **explainable behavioral analysis first, richer longitudinal intelligence second.**

See [docs/roadmap.md](docs/roadmap.md) for the current roadmap.

## What I learned building it

TradeMind AI was one of the projects that pushed me from "building a feature" toward thinking about:

- product behavior, not just code
- explainability vs. black-box intelligence
- local-first data handling
- integrations between a core application and agent workflows
- building a demo that communicates the product quickly

---

**Built by [@Mrblank254](https://x.com/Mrblank254)**
