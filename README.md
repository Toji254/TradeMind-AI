# TradeMind AI - Behavioral Trading Psychology Assistant

TradeMind AI is a privacy-first, local-first assistant that analyzes your trading behavior on Binance to uncover emotional patterns like FOMO, panic selling, and revenge trading.

## 🚀 Step-by-Step Setup Guide

### 1. Prerequisites
- **Python 3.14+** installed.
- **Git** installed.
- **Binance API Keys** (Read-only recommended).

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/trademind-ai.git
cd TradeMind-AI
```

### 3. Set Up Virtual Environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
# If using the automation demo features:
playwright install chromium
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your settings:
```bash
cp .env.example .env
```
Open `.env` and add your Binance API keys if you want them to be pre-loaded.

### 6. Initialize Database
```bash
python -m src.app.cli init
```

### 7. Run the Application
#### Web Dashboard (Recommended)
```bash
python -m src.app.cli serve-web
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

#### CLI Commands
- **Check Configuration:** `python -m src.app.cli doctor`
- **Sync Trades:** `python -m src.app.cli sync-binance --symbol BTCUSDT --limit 50 --market spot`
- **Analyze Behavior:** `python -m src.app.cli analyze-local --symbol BTCUSDT`
- **Coaching Plan:** `python -m src.app.cli coaching-plan --symbol BTCUSDT`

## 📊 Key Features
- **Behavioral Score:** A real-time discipline index based on your recent trades.
- **Pattern Detection:** Identifies FOMO buys, panic sells, and revenge trading using SMA-based logic.
- **Coaching Summary:** Generates actionable psychology guardrails to help you stay disciplined.
- **Local SQLite Storage:** Your trade history and journal notes never leave your machine.
- **Telegram Integration:** Get real-time alerts when new behavioral insights are ready.

## 🔒 Privacy & Security
- **Local First:** All analysis and trade storage happen on your local machine.
- **Read-Only Keys:** TradeMind AI only requires **Read-Only** API access. It never executes trades or withdraws funds.
- **UI Key Management:** You can now enter your API keys directly in the web dashboard for a seamless setup.

## 🛠️ Tech Stack
- **Backend:** FastAPI, Typer
- **Database:** SQLite, SQLAlchemy
- **Analysis:** Pandas, NumPy, VaderSentiment
- **Frontend:** HTML/CSS (OKX-inspired dark mode), Chart.js
- **Integrations:** Binance (ccxt/requests), Telegram Bot API

## 📝 License
MIT License. See `LICENSE` for details.
