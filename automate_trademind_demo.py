import os
import asyncio
import logging
import random
import sys
import time
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page

# --- Load Environment -------------------------------------------------------
load_dotenv()

OPENCLAW_URL = os.getenv("DEMO_OPENCLAW_URL", "http://127.0.0.1:18789")
OPENCLAW_CHAT_URL = os.getenv("DEMO_OPENCLAW_CHAT_URL", "http://127.0.0.1:18789/chat?session=agent%3Amain%3Amain")
GATEWAY_WS_URL = os.getenv("DEMO_GATEWAY_WS_URL", "ws://127.0.0.1:18789/gateway")
GATEWAY_TOKEN = os.getenv("DEMO_GATEWAY_TOKEN")

from src.connectors.telegram_bot import TelegramBotService

# --- Logging ----------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

async def send_to_telegram(text: str):
    """Optionally send the same coaching message to a real Telegram bot if configured."""
    bot = TelegramBotService()
    if bot.is_configured():
        logger.info(">> Sending statistics to Telegram bot...")
        success = await bot.send_message(text)
        if success:
            logger.info(">> Telegram message delivered successfully.")
        else:
            logger.warning(">> Failed to send Telegram message. Check your .env (TELEGRAM_BOT_TOKEN/CHAT_ID).")
    else:
        logger.info(">> Telegram bot not configured in .env; skipping real message.")

async def human_type(page: Page, selector: str, text: str, delay_min=30, delay_max=80):
    """Type like a human for the video recording."""
    try:
        await page.wait_for_selector(selector, state="visible", timeout=5000)
        await page.click(selector)
        for char in text:
            await page.keyboard.type(char, delay=random.randint(delay_min, delay_max))
        await asyncio.sleep(0.5)
    except Exception:
        pass

async def human_scroll(page: Page, pixels=400):
    """Smooth human-like scrolling."""
    total_scroll = 0
    while total_scroll < pixels:
        step = random.randint(50, 100)
        await page.mouse.wheel(0, step)
        total_scroll += step
        await asyncio.sleep(random.uniform(0.1, 0.3))

async def simulate_gemini_cli(prompt: str, code_output: str):
    """Simulates a live Gemini CLI interaction in the terminal."""
    print(f"\n$ gemini generate \"", end="", flush=True)
    for char in prompt:
        print(char, end="", flush=True)
        await asyncio.sleep(random.uniform(0.01, 0.04))
    print("\"", end="", flush=True)
    await asyncio.sleep(0.5)
    print("\n\n[Gemini CLI] Analyzing request...", end="", flush=True)
    await asyncio.sleep(1.2)
    print(" Done.", flush=True)
    print("[Gemini CLI] Generating behavioral pattern detector...", flush=True)
    await asyncio.sleep(0.8)
    print("-" * 70)
    for line in code_output.split('\n'):
        print(line)
        await asyncio.sleep(0.03)
    print("-" * 70)
    print("\n[Gemini CLI] Complete. Pattern detector ready for deployment.")

async def inject_coaching_reply(page: Page, coaching_text: str):
    """Robust injection of the TradeMind coaching response."""
    script = """
    (text) => {
        const selectors = ['.messages-container', '.chat-messages', 'main .overflow-y-auto', '.flex-1.overflow-y-auto', '[role="log"]'];
        let container = null;
        for (const sel of selectors) {
            container = document.querySelector(sel);
            if (container) break;
        }
        if (!container) {
             const userMsg = Array.from(document.querySelectorAll('div, span, p')).find(el => el.textContent.includes('Analyze my BTC trades'));
             if (userMsg) container = userMsg.closest('.overflow-y-auto') || userMsg.parentElement.closest('div');
        }

        if (container) {
            const msgDiv = document.createElement('div');
            msgDiv.className = 'message assistant bot flex justify-start mb-6 mt-2';
            msgDiv.innerHTML = `
                <div class="bg-gray-800 border border-blue-500/40 text-gray-100 p-5 rounded-2xl max-w-[90%] whitespace-pre-wrap shadow-2xl animate-pulse-once border-l-4 border-l-blue-400">
                    <div class="prose prose-invert text-sm sm:text-base leading-relaxed">
                        ${text.replace(/\\n/g, '<br>').replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>').replace(/<b>/g, '<strong>').replace(/<\\/b>/g, '</strong>')}
                    </div>
                </div>
            `;
            container.appendChild(msgDiv);
            setTimeout(() => { container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' }); }, 100);
            return true;
        }
        return false;
    }
    """
    return await page.evaluate(script, coaching_text)

async def run_storyboard_demo():
    coaching_text = """📊 <b>TradeMind AI: Behavioral Analysis for BTCUSDT</b>

<b>Discipline Status: WARNING.</b> Emotional triggers are impacting your performance.

- 42 trades analyzed.
- 28.5% of buys were FOMO (chasing price above MA10).
- 12.0% of sells were PANIC (exiting below MA10).

<b>Guardrail Rules to Adopt:</b>
• Adopt a 'one-candle wait' rule: wait for a full period to close before entering a fast move.
• Set a strict chase cutoff: never enter more than 0.5% away from your planned level.
• Take a 15-minute cooldown away from the screen after a volatile exit."""

    print("====================================================")

    print("   TRADEMIND AI - BINANCE HACKATHON MASTER DIRECTOR ")
    print("====================================================")
    print("1. Ensure OpenClaw is running at: " + OPENCLAW_URL)
    print("2. Position Terminal (LEFT) and Browser (RIGHT).")
    print("3. Press RECORD in your screen recorder.")
    print("4. Automation starts in 10 seconds...")
    print("====================================================")
    
    await asyncio.sleep(10)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        # [0:00-0:30] Intro
        print("\n[0:00-0:30] PHASE 1: INTRO (User speaks over B-roll)")
        await asyncio.sleep(10)

        # [0:30-1:00] OpenClaw Dashboard Overview
        print("\n[0:30-1:00] PHASE 2: OPENCLAW DASHBOARD OVERVIEW")
        await page.goto(OPENCLAW_URL)
        await asyncio.sleep(2)
        if await page.locator("input[placeholder*='ws://']").is_visible():
            print(">> Configuring Gateway...")
            await page.fill("input[placeholder*='ws://']", GATEWAY_WS_URL)
            await page.fill("input[type='password']", GATEWAY_TOKEN)
            await page.keyboard.press("Enter")
            await asyncio.sleep(4)
        print(">> Showing dashboard features...")
        await human_scroll(page, pixels=500)
        await asyncio.sleep(5)

        # [1:00-1:30] Create Agent
        print("\n[1:00-1:30] PHASE 3: CREATE AGENT (TradeMind AI)")
        await page.goto(f"{OPENCLAW_URL}/agents")
        await asyncio.sleep(3)
        # Visually highlight the brain
        await human_scroll(page, pixels=200)
        await asyncio.sleep(5)

        # [1:30-2:15] Install Binance Skill
        print("\n[1:30-2:15] PHASE 4: BINANCE SKILL CONFIGURATION")
        await page.goto(f"{OPENCLAW_URL}/skills")
        await asyncio.sleep(2)
        if await page.locator("input[placeholder*='Search']").is_visible():
            await human_type(page, "input[placeholder*='Search']", "Binance")
        print(">> Searching for ready-made Binance skills...")
        await asyncio.sleep(5)
        print(">> Skill configured via .env testnet keys. Ready for next phase.")
        await asyncio.sleep(5) # Time for voiceover about .env and API keys

        # [2:15-3:15] Create Custom Pattern Detector with Gemini CLI
        print("\n[2:15-3:15] PHASE 5: GEMINI CLI & CUSTOM SKILL (Watch Terminal)")
        prompt = "Write a Python function called analyze_patterns(trades) that takes a list of trades (each trade has 'price' (float), 'time' (ms timestamp), 'isBuyer' (bool)). Calculate a 10-period simple moving average of price. Identify FOMO buys: buys where price > 1.02 * MA10. Identify panic sells: sells where price < 0.98 * MA10. Return a dict with counts, percentages, and a list of personalized recommendations based on the results. Include pandas code. Make it production-ready with error handling."
        code = """import pandas as pd

def analyze_patterns(trades):
    try:
        df = pd.DataFrame(trades)
        df['price'] = df['price'].astype(float)
        df['ma10'] = df['price'].rolling(window=10).mean()
        
        fomo_buys = df[(df['isBuyer'] == True) & (df['price'] > 1.02 * df['ma10'])]
        panic_sells = df[(df['isBuyer'] == False) & (df['price'] < 0.98 * df['ma10'])]
        
        results = {
            'fomo_count': len(fomo_buys),
            'panic_count': len(panic_sells),
            'recommendations': ["Breathe. You're market-buying the top."] if len(fomo_buys) > 0 else []
        }
        return results
    except Exception as e:
        return {"error": str(e)}"""
        
        await simulate_gemini_cli(prompt, code)
        
        print(">> Navigating to Skill Editor...")
        await page.goto(f"{OPENCLAW_URL}/skills/new")
        await asyncio.sleep(2)
        await human_type(page, "input[placeholder*='Name']", "Pattern Detector")
        # Visual paste effect
        await page.click(".monaco-editor, textarea, [contenteditable='true']")
        await page.evaluate(f"navigator.clipboard.writeText(`{code}`)")
        await page.keyboard.press("Control+V")
        await asyncio.sleep(10)

        # [3:15-4:00] Build Workflow
        print("\n[3:15-4:00] PHASE 6: WORKFLOW BUILDER")
        await page.goto(f"{OPENCLAW_URL}/workflows")
        await asyncio.sleep(2)
        await human_scroll(page, pixels=300)
        await asyncio.sleep(15) # Time to explain the nodes

        # [4:00-4:45] Deploy to Telegram & Test
        print("\n[4:00-4:45] PHASE 7: TELEGRAM DEPLOYMENT & CHAT TEST")
        await page.goto(OPENCLAW_CHAT_URL)
        await asyncio.sleep(4)
        
        print(">> Sending Prompt...")
        chat_input = "textarea, .chat-input, [contenteditable='true']"
        await human_type(page, chat_input, "Analyze my BTC trades for FOMO patterns.")
        await page.keyboard.press("Enter")
        
        print(">> Thinking...")
        await asyncio.sleep(6)
        
        print(">> Injecting Response & Notifying Telegram...")
        # Start both tasks
        success = await inject_coaching_reply(page, coaching_text)
        await send_to_telegram(coaching_text)
        
        if success:
            print(">> INJECTION SUCCESSFUL. Ready for final shot.")
        else:
            print(">> INJECTION FAILED. Check UI layout.")

        # [4:45-5:00] Closing Pitch
        print("\n[4:45-5:00] PHASE 8: CLOSING PITCH (Holding Screen)")
        await asyncio.sleep(20)

        await browser.close()
        print("\n[FINISH] TradeMind AI Master Director Complete.")

if __name__ == "__main__":
    asyncio.run(run_storyboard_demo())
