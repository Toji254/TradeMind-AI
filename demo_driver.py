import asyncio
import os
import subprocess
import time
import socket
import random
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# Configuration
OPENCLAW_URL = os.getenv("DEMO_OPENCLAW_URL", "http://127.0.0.1:18789")
OPENCLAW_CHAT_URL = os.getenv("DEMO_OPENCLAW_CHAT_URL", "http://127.0.0.1:18789/chat?session=agent%3Amain%3Amain")
GATEWAY_WS_URL = os.getenv("DEMO_GATEWAY_WS_URL", "ws://127.0.0.1:18789")
GATEWAY_TOKEN = os.getenv("DEMO_GATEWAY_TOKEN")

def wait_for_port(port, host='127.0.0.1', timeout=20):
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(1)
            if time.time() - start_time > timeout:
                return False

async def human_type(page, selector, text, delay_min=30, delay_max=80):
    try:
        await page.wait_for_selector(selector, state="visible", timeout=5000)
        await page.click(selector)
        for char in text:
            await page.keyboard.type(char, delay=random.randint(delay_min, delay_max))
        await asyncio.sleep(0.5)
    except Exception:
        pass

async def human_scroll(page, pixels=300, delay_range=(2, 5)):
    total_scroll = 0
    while total_scroll < pixels:
        scroll_step = random.randint(50, 150)
        await page.mouse.wheel(0, scroll_step)
        total_scroll += scroll_step
        await asyncio.sleep(random.uniform(delay_range[0], delay_range[1]) / 10)
    await asyncio.sleep(random.uniform(0.5, 1.5))

async def simulate_gemini_cli(prompt, code_output):
    """Simulates the Gemini CLI interaction in the terminal."""
    print(f"\n$ gemini generate \"", end="", flush=True)
    for char in prompt:
        print(char, end="", flush=True)
        await asyncio.sleep(random.uniform(0.01, 0.04))
    print("\"", end="", flush=True)
    await asyncio.sleep(0.5)
    print("\n\n[Gemini CLI] Analyzing request...", end="", flush=True)
    await asyncio.sleep(1.2)
    print(" Done.", flush=True)
    print("[Gemini CLI] Generating pattern detector code...", flush=True)
    await asyncio.sleep(0.8)
    print("-" * 60)
    for line in code_output.split('\n'):
        print(line)
        await asyncio.sleep(0.03)
    print("-" * 60)
    print("\n[Gemini CLI] Complete. Ready for deployment.")

async def inject_coaching_reply(page):
    """Robust injection of the TradeMind coaching response."""
    coaching_text = """📊 **TradeMind AI: Behavioral Analysis for BTCUSDT**

**Discipline Status: WARNING.** Emotional triggers are impacting your performance.

- 42 trades analyzed.
- 28.5% of buys were FOMO (chasing price above MA10).
- 12.0% of sells were PANIC (exiting below MA10).

**Guardrail Rules to Adopt:**
* Adopt a 'one-candle wait' rule: wait for a full period to close before entering a fast move.
* Set a strict chase cutoff: never enter more than 0.5% away from your planned level.
* Take a 15-minute cooldown away from the screen after a volatile exit."""

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
                        ${text.replace(/\\n/g, '<br>').replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')}
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

async def run_detailed_demo():
    print("====================================================")
    print("   TRADEMIND AI - BINANCE HACKATHON DEMO DIRECTOR   ")
    print("====================================================")
    print("1. Ensure OpenClaw is running at: http://127.0.0.1:18789")
    print("2. Position Terminal (LEFT) and Browser (RIGHT).")
    print("3. Start Recording.")
    print("4. Autopilot starts in 5 seconds...")
    print("====================================================")
    
    await asyncio.sleep(5)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        # [0:00-0:30] Intro
        print("\n[0:00-0:30] PHASE 1: INTRO")
        await asyncio.sleep(5)

        # [0:30-1:00] Dashboard Overview
        print("\n[0:30-1:00] PHASE 2: OPENCLAW DASHBOARD")
        await page.goto(OPENCLAW_URL)
        await asyncio.sleep(2)
        if await page.locator("input[placeholder*='ws://']").is_visible():
            if not GATEWAY_TOKEN:
                raise RuntimeError("DEMO_GATEWAY_TOKEN is required when the local OpenClaw gateway asks for authentication.")
            await page.fill("input[placeholder*='ws://']", GATEWAY_WS_URL)
            await page.fill("input[type='password']", GATEWAY_TOKEN)
            await page.keyboard.press("Enter")
            await asyncio.sleep(4)
        await human_scroll(page, pixels=400)

        # [1:00-1:30] Create Agent
        print("\n[1:00-1:30] PHASE 3: CREATE AGENT (TradeMind AI)")
        await page.goto(f"{OPENCLAW_URL}/agents")
        await asyncio.sleep(2)
        # Visually show the 'main' agent or creation UI
        await human_scroll(page, pixels=200)

        # [1:30-2:15] Binance Skill
        print("\n[1:30-2:15] PHASE 4: INSTALL BINANCE SKILL")
        await page.goto(f"{OPENCLAW_URL}/skills")
        await asyncio.sleep(2)
        if await page.locator("input[placeholder*='Search']").is_visible():
            await human_type(page, "input[placeholder*='Search']", "Binance")
        await asyncio.sleep(3)

        # [2:15-3:15] Gemini CLI
        print("\n[2:15-3:15] PHASE 5: GEMINI CLI INTERACTION (Look at Terminal!)")
        prompt = "Write a Python function called analyze_patterns(trades)..."
        code = """import pandas as pd
def analyze_patterns(trades):
    df = pd.DataFrame(trades)
    df['ma10'] = df['price'].rolling(window=10).mean()
    fomo = df[(df['isBuyer']) & (df['price'] > 1.02 * df['ma10'])]
    panic = df[(~df['isBuyer']) & (df['price'] < 0.98 * df['ma10'])]
    return {"fomo": len(fomo), "panic": len(panic)}"""
        await simulate_gemini_cli(prompt, code)
        
        # Paste visual
        print(">> Pasting into Skill Editor...")
        await page.goto(f"{OPENCLAW_URL}/skills/new")
        await asyncio.sleep(2)
        await human_type(page, "input[placeholder*='Name']", "Pattern Detector")
        await page.click(".monaco-editor, textarea")
        await page.evaluate(f"navigator.clipboard.writeText(`{code}`)")
        await page.keyboard.press("Control+V")
        await asyncio.sleep(4)

        # [3:15-4:00] Build Workflow
        print("\n[3:15-4:00] PHASE 6: WORKFLOW BUILDER")
        await page.goto(f"{OPENCLAW_URL}/workflows")
        await asyncio.sleep(5)

        # [4:00-4:45] Deploy to Telegram & Test
        print("\n[4:00-4:45] PHASE 7: TELEGRAM CHAT TEST")
        await page.goto(OPENCLAW_CHAT_URL)
        await asyncio.sleep(3)
        await human_type(page, "textarea, .chat-input", "Analyze my BTC trades for FOMO patterns.")
        await page.keyboard.press("Enter")
        await asyncio.sleep(4)
        await inject_coaching_reply(page)
        print(">> COACHING DELIVERED.")

        # [4:45-5:00] Closing
        print("\n[4:45-5:00] PHASE 8: CLOSING PITCH")
        await asyncio.sleep(15)

        await browser.close()
        print("\nDemo Director Complete.")

if __name__ == "__main__":
    asyncio.run(run_detailed_demo())
