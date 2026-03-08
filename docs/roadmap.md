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
- [ ] support time-range and symbol filtering from exchange
- [ ] add futures testnet sync

## Phase 3 - Analysis Pipeline

- [x] load synced trades from SQLite
- [x] add local symbol discovery
- [x] analyze local history through detector pipeline
- [x] generate coaching-style reports
- [ ] add richer behavioral detectors
- [ ] improve trade outcome inference

## Phase 4 - Coaching Layer

- [ ] generate intervention suggestions tied to specific patterns
- [ ] add journaling input + sentiment tagging
- [ ] track repeated behaviors over time

## Phase 5 - OpenClaw Experience

- [ ] create OpenClaw-facing skill/workflow
- [ ] support conversational analysis requests
- [ ] schedule daily mindset prompts and reminders

## Phase 6 - Advanced Features

- [ ] anomaly detection
- [ ] progress dashboard
- [ ] opt-in anonymized research workflows
