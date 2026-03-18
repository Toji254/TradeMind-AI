from __future__ import annotations

import asyncio
import logging
import re
from typing import Dict, Any

from src.connectors.telegram_bot import TelegramBotService
from src.app.services import TradeMindService
from src.app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TradeMindBot")

# Simple in-memory "transit" for user-pushed keys (simulating a session)
# Structure: {chat_id: {"spot": {"api_key": ..., "api_secret": ...}, "futures": {"api_key": ..., "api_secret": ...}}}
KEY_TRANSIT: Dict[int, Dict[str, Any]] = {}

class TradeMindBot:
    def __init__(self):
        self.bot = TelegramBotService()
        self.service = TradeMindService()
        self.is_running = False

    async def start(self):
        if not self.bot.token:
            logger.error("TELEGRAM_BOT_TOKEN not set in environment.")
            return

        # Register commands with Telegram UI
        commands = [
            {"command": "start", "description": "Get started with TradeMind AI"},
            {"command": "connect", "description": "Connect Binance [spot|futures] KEY SECRET"},
            {"command": "progress", "description": "Check [spot|futures] balance & PNL"},
            {"command": "brief", "description": "Behavioral score summary"},
            {"command": "guardrails", "description": "Active discipline rules"},
            {"command": "journal", "description": "Add a private note"},
            {"command": "mood", "description": "Trading mood assessment"},
            {"command": "status", "description": "Check session connection"},
            {"command": "help", "description": "Show all commands"},
        ]
        await self.bot.set_commands(commands)

        logger.info("TradeMind Bot started. Waiting for messages...")
        self.is_running = True
        
        while self.is_running:
            updates = await self.bot.get_updates()
            for update in updates:
                await self.handle_update(update)
            await asyncio.sleep(1)

    async def handle_update(self, update: Dict[str, Any]):
        message = update.get("message")
        if not message:
            return

        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user = message["from"].get("username", "Trader")

        # Command Dispatcher
        parts = text.split()
        if not parts: return
        cmd = parts[0].lower()

        if cmd == "/start":
            await self.cmd_start(chat_id, user)
        elif cmd == "/connect":
            await self.cmd_connect(chat_id, text)
        elif cmd == "/progress":
            await self.cmd_progress(chat_id, text)
        elif cmd == "/brief":
            await self.cmd_brief(chat_id)
        elif cmd == "/guardrails":
            await self.cmd_guardrails(chat_id)
        elif cmd == "/journal":
            await self.cmd_journal(chat_id, text)
        elif cmd == "/status":
            await self.cmd_status(chat_id)
        elif cmd == "/mood":
            await self.cmd_mood(chat_id)
        elif cmd == "/help":
            await self.cmd_help(chat_id)
        else:
            # Check for tm commands (passing to bridge logic)
            from src.app.openclaw_bridge import handle_trademind_command
            if text.lower().startswith("tm "):
                reply = handle_trademind_command(text)
                await self.bot.send_message(reply, chat_id=chat_id)
            else:
                await self.bot.send_message(
                    "🤖 I'm listening! Type /help to see available commands or use <code>tm brief</code> for analysis.",
                    chat_id=chat_id
                )

    async def cmd_start(self, chat_id: int, user: str):
        welcome = (
            f"Welcome, {user}! 🧠 I am your <b>TradeMind AI</b> coach.\n\n"
            "I help you stay disciplined by analyzing your Binance behavior locally.\n\n"
            "<b>Quick Setup:</b>\n"
            "• <code>/connect spot KEY SECRET</code>\n"
            "• <code>/connect futures KEY SECRET</code>\n\n"
            "<b>Trading Progress:</b>\n"
            "Type <code>/progress spot</code> to see your balance and assets."
        )
        await self.bot.send_message(welcome, chat_id=chat_id)

    async def cmd_connect(self, chat_id: int, text: str):
        parts = text.split()
        if len(parts) != 4 or parts[1].lower() not in ["spot", "futures"]:
            await self.bot.send_message(
                "❌ Usage: <code>/connect [spot|futures] KEY SECRET</code>",
                chat_id=chat_id
            )
            return

        market = parts[1].lower()
        api_key = parts[2]
        api_secret = parts[3]

        if chat_id not in KEY_TRANSIT:
            KEY_TRANSIT[chat_id] = {}
        
        KEY_TRANSIT[chat_id][market] = {
            "api_key": api_key,
            "api_secret": api_secret
        }

        await self.bot.send_message(
            f"✅ <b>{market.title()} Keys Connected!</b>\n"
            "You can now use <code>/progress</code> or claim these in the dashboard.",
            chat_id=chat_id
        )
        logger.info(f"User {chat_id} pushed {market} keys.")

    async def _get_user_creds(self, chat_id: int, market: str):
        """Helper to get keys from transit or env."""
        from src.connectors.binance_client import BinanceCredentials
        
        # Check transit first
        if chat_id in KEY_TRANSIT and market in KEY_TRANSIT[chat_id]:
            creds = KEY_TRANSIT[chat_id][market]
            return BinanceCredentials(
                api_key=creds["api_key"],
                api_secret=creds["api_secret"],
                base_url=settings.binance_spot_base_url if market == "spot" else settings.binance_futures_base_url
            )
        
        # Fallback to env (only if chat_id matches configured one)
        if str(chat_id) == settings.telegram_chat_id:
            if market == "spot" and settings.binance_spot_api_key:
                return BinanceCredentials(
                    api_key=settings.binance_spot_api_key,
                    api_secret=settings.binance_spot_api_secret,
                    base_url=settings.binance_spot_base_url
                )
            if market == "futures" and settings.binance_futures_api_key:
                return BinanceCredentials(
                    api_key=settings.binance_futures_api_key,
                    api_secret=settings.binance_futures_api_secret,
                    base_url=settings.binance_futures_base_url
                )
        return None

    async def cmd_progress(self, chat_id: int, text: str):
        parts = text.split()
        market = parts[1].lower() if len(parts) > 1 else "spot"
        if market not in ["spot", "futures"]: market = "spot"

        creds = await self._get_user_creds(chat_id, market)
        if not creds:
            await self.bot.send_message(f"❌ No {market} keys found. Use /connect first.", chat_id=chat_id)
            return

        await self.bot.send_message(f"⏳ Fetching your {market} progress...", chat_id=chat_id)
        try:
            snapshot = self.service.get_account_snapshot(market=market, credentials=creds)
            if market == "spot":
                msg = (
                    f"💰 <b>Spot Account Progress</b>\n"
                    f"Total Est: <code>{snapshot['estimated_total_usdt']:.2f} USDT</code>\n"
                    f"Assets: {snapshot['asset_count']}\n"
                    f"Top Asset: {snapshot['top_asset']} ({snapshot['top_asset_pct']:.1f}%)"
                )
            else:
                msg = (
                    f"📈 <b>Futures Account Progress</b>\n"
                    f"Wallet: <code>{snapshot['wallet_balance']:.2f} USDT</code>\n"
                    f"Unrealized PNL: <code>{snapshot['unrealized_profit']:.2f} USDT</code>\n"
                    f"Margin Ratio: {snapshot['margin_ratio']:.2f}%"
                )
            await self.bot.send_message(msg, chat_id=chat_id)
        except Exception as e:
            await self.bot.send_message(f"❌ Error fetching progress: {str(e)}", chat_id=chat_id)

    async def cmd_brief(self, chat_id: int):
        await self.bot.send_message("📊 Analyzing your recent behavior...", chat_id=chat_id)
        try:
            summary = self.service.analyze_local() # Uses local DB history
            score = summary.get("behavioral_score", 50)
            status = "🟢 Disciplined" if score > 70 else "🟡 Average" if score > 40 else "🔴 Impulsive"
            
            msg = (
                f"🧠 <b>Behavioral Brief</b>\n"
                f"Discipline Score: <b>{score}</b> ({status})\n"
                f"Trades Analyzed: {summary['trade_count']}\n"
                f"FOMO Signals: {summary['fomo_buy_count']}\n"
                f"Panic Signals: {summary['panic_sell_count']}\n\n"
                f"<i>Latest Insight: {summary['insights'][0] if summary['insights'] else 'Keep it up!'}</i>"
            )
            await self.bot.send_message(msg, chat_id=chat_id)
        except Exception as e:
            await self.bot.send_message(f"❌ Analysis failed: {str(e)}", chat_id=chat_id)

    async def cmd_guardrails(self, chat_id: int):
        from src.analysis.engine import AnalysisEngine
        from src.coaching.interventions import build_intervention_plan
        from src.storage.local_db import load_trades
        
        trades = load_trades(settings.db_path, limit=50)
        results = AnalysisEngine().run(trades)
        plan = build_intervention_plan(results)
        
        if not plan:
            await self.bot.send_message("✅ No active guardrails. You're trading within safe emotional bounds!", chat_id=chat_id)
            return

        msg = "🛡️ <b>Active Guardrails</b>\n\n" + "\n".join([f"• {item}" for item in plan])
        await self.bot.send_message(msg, chat_id=chat_id)

    async def cmd_journal(self, chat_id: int, text: str):
        content = text.replace("/journal", "").strip()
        if not content:
            await self.bot.send_message("📝 Use: <code>/journal Your thoughts here...</code>", chat_id=chat_id)
            return
        
        from src.storage.local_db import add_journal_entry
        add_journal_entry(settings.db_path, tag="telegram", text=content)
        await self.bot.send_message("✅ Journal entry saved to your local database.", chat_id=chat_id)

    async def cmd_status(self, chat_id: int):
        has_spot = chat_id in KEY_TRANSIT and "spot" in KEY_TRANSIT[chat_id]
        has_futures = chat_id in KEY_TRANSIT and "futures" in KEY_TRANSIT[chat_id]
        status = (
            "📊 <b>TradeMind Session Status</b>\n"
            f"Chat ID: <code>{chat_id}</code>\n"
            f"Spot Connected: {'✅' if has_spot else '❌'}\n"
            f"Futures Connected: {'✅' if has_futures else '❌'}"
        )
        await self.bot.send_message(status, chat_id=chat_id)

    async def cmd_mood(self, chat_id: int):
        from src.storage.local_db import load_journal_entries
        entries = load_journal_entries(settings.db_path, limit=5)
        if not entries:
            await self.bot.send_message("📝 Your journal is empty. Add a note with <code>/journal</code> first!", chat_id=chat_id)
            return
        
        avg_sentiment = sum(e.sentiment_compound for e in entries) / len(entries)
        mood = "Confident 🚀" if avg_sentiment > 0.4 else "Balanced ⚖️" if avg_sentiment > -0.1 else "Stressed 😰"
        
        msg = (
            f"🧠 <b>Trading Mood Assessment</b>\n"
            f"Recent Tone: <b>{mood}</b>\n"
            f"Sentiment Index: <code>{avg_sentiment:+.2f}</code>\n\n"
            f"<i>Recent Note: \"{entries[0].text[:60]}...\"</i>"
        )
        await self.bot.send_message(msg, chat_id=chat_id)

    async def cmd_help(self, chat_id: int):
        help_text = (
            "🧠 <b>TradeMind AI Bot - Command Guide</b>\n\n"
            "<b>Setup & Session:</b>\n"
            "• /start - Get started and see welcome message.\n"
            "• /connect [spot|futures] KEY SECRET - Push your Binance keys to the local dashboard session.\n"
            "• /status - Check if your API keys are currently connected in this session.\n\n"
            "<b>Trading & Progress:</b>\n"
            "• /progress spot - Check your spot balance and top asset distribution.\n"
            "• /progress futures - Check your futures wallet, unrealized PNL, and margin ratio.\n\n"
            "<b>Psychology & Discipline:</b>\n"
            "• /brief - Get a quick behavioral discipline score and recent FOMO/Panic stats.\n"
            "• /guardrails - View the active emotional rules suggested for your current trading state.\n"
            "• /journal [text] - Quickly log a thought or feeling to your local psychology journal.\n"
            "• /mood - Assess your recent trading mindset based on journal sentiment.\n\n"
            "<b>Analysis (OpenClaw):</b>\n"
            "• <code>tm brief</code> - Generate a detailed text-based report of your account.\n"
            "• <code>tm analyze BTCUSDT</code> - Sync and perform full behavioral analysis on a specific pair."
        )
        await self.bot.send_message(help_text, chat_id=chat_id)

if __name__ == "__main__":
    bot_app = TradeMindBot()
    asyncio.run(bot_app.start())
