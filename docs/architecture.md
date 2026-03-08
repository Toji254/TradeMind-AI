# TradeMind AI Architecture

## Product Direction

TradeMind AI is a local-first behavioral analysis and coaching system for traders.

The system is designed to answer one question well:

> What destructive patterns does this trader repeat, and how can we interrupt them before they become habits?

## High-Level Components

### 1. Connectors
Responsible for ingesting user-authorized data.

Current:
- Binance Spot Testnet account/trade access

Planned:
- Binance Futures Testnet
- CSV imports
- Bybit
- OKX

### 2. Storage
Persists normalized local data.

- SQLite database for trades and journal entries
- local secrets/config for exchange credentials
- no cloud storage required for v1

### 3. Analysis
Behavior detection and profiling.

Current detectors:
- FOMO buy detector
- panic sell detector
- revenge trading detector
- streak behavior detector
- time-of-day bias detector
- overtrading detector

### 4. Coaching
Converts detected patterns into useful language and practical next steps.

Current outputs:
- coaching-style summaries
- intervention plans
- behavioral discipline score
- journal-aware reflections

### 5. Reports
Produces summaries for CLI, OpenClaw chat delivery, and future dashboards.

## Core Data Flow

1. fetch trade history from Binance
2. normalize into internal trade model
3. save locally in SQLite
4. optionally store journal entries with sentiment scoring
5. run detectors against selected time windows
6. aggregate findings into a behavioral profile
7. generate coaching output and guardrail suggestions
8. deliver insight via CLI/OpenClaw

## Engineering Principles

- prefer explainable rules first
- keep exchange-specific logic isolated
- design for local-only operation
- maintain testable detector contracts
- avoid overengineering ML early
- keep outputs usable in both human and machine-readable forms
