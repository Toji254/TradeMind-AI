# TradeMind AI Architecture

## Product Direction

TradeMind AI is a local-first behavioral analysis and coaching system for traders.

The system is designed to answer one question well:

> What destructive patterns does this trader repeat, and how can we interrupt them before they become habits?

## High-Level Components

### 1. Connectors
Responsible for ingesting user-authorized data.

Initial target:
- Binance trade history

Future targets:
- CSV imports
- Bybit
- OKX
- journaling channels

### 2. Storage
Persists normalized local data.

- SQLite database for trades, notes, analyses, and interventions
- local secrets/config for exchange credentials
- no cloud storage required for MVP

### 3. Analysis
Behavior detection and profiling.

Sub-layers:
- rule-based detectors
- statistical summaries
- optional ML clustering/anomaly detection later

### 4. Coaching
Converts detected patterns into useful language and practical next steps.

Examples:
- reflection prompts
- anti-impulse rules
- cooldown suggestions
- pre-trade reminders

### 5. Reports
Produces summaries for CLI, OpenClaw chat delivery, and future dashboards.

## Core Data Flow

1. fetch trade history from Binance
2. normalize into internal trade model
3. save locally
4. run detectors against selected time windows
5. aggregate findings into a profile
6. generate coaching output
7. deliver insight via CLI/OpenClaw

## MVP Detector Set

- FOMO buy detector
- panic sell detector
- revenge trading detector
- time-of-day bias detector
- streak behavior detector

## Engineering Principles

- prefer explainable rules first
- keep exchange-specific logic isolated
- design for local-only operation
- maintain testable detector contracts
- avoid overengineering ML early
