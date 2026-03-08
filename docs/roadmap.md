# TradeMind AI Roadmap

## Phase 1 - MVP Foundation

- [x] initialize repository
- [x] define product direction
- [x] scaffold core modules
- [x] implement local config and SQLite storage
- [x] add normalized trade schema
- [x] build first behavior detectors
- [x] create CLI commands for health checks and demo analysis

## Phase 2 - Exchange Integration

- [x] integrate Binance spot testnet trade fetch/sync
- [x] store trade history locally
- [x] wire futures-ready testnet sync path
- [ ] provide futures testnet credentials and validate live sync
- [ ] support time-range filtering from exchange

## Phase 3 - Analysis Pipeline

- [x] load synced trades from SQLite
- [x] add local symbol discovery
- [x] analyze local history through detector pipeline
- [x] generate coaching-style reports
- [x] add richer behavioral detectors
- [x] add chart-ready local analytics datasets
- [ ] improve trade outcome inference

## Phase 4 - Coaching Layer

- [x] generate intervention suggestions tied to specific patterns
- [x] add journaling input + sentiment tagging
- [ ] track repeated behaviors over time

## Phase 5 - Product Experience

- [x] create a polished dark-mode web UI
- [x] restyle the UI toward an OKX-like dark terminal feel
- [x] support local sync + analysis from the dashboard
- [x] expose journal capture in the UI
- [x] add chart panels to the dashboard
- [ ] add trend history and weekly review cards

## Phase 6 - OpenClaw Experience

- [ ] create OpenClaw-facing skill/workflow
- [ ] support conversational analysis requests
- [ ] schedule daily mindset prompts and reminders

## Phase 7 - Advanced Features

- [ ] anomaly detection
- [ ] progress dashboard history
- [ ] opt-in anonymized research workflows
