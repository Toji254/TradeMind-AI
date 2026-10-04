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

# API Keys (Pre-filled for demo)
BINANCE_API_KEY = os.getenv("BINANCE_SPOT_API_KEY", "hackathon-demo-key")
BINANCE_API_SECRET = os.getenv("BINANCE_SPOT_API_SECRET", "hackathon-demo-secret")

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
        pass # Fail silently to keep demo moving

async def human_scroll(page, pixels=300, delay_range=(2, 5)):
    total_scroll = 0
    while total_scroll < pixels:
        scroll_step = random.randint(50, 150)
        await page.mouse.wheel(0, scroll_step)
        total_scroll += scroll_step
        await asyncio.sleep(random.uniform(delay_range[0], delay_range[1]) / 10)
    await asyncio.sleep(random.uniform(0.5, 1.5))

async def simulate_gemini_cli(prompt, code_output):
    """Simulates a live CLI typing effect in the terminal."""
    print(f"\n$ gemini generate \"", end="", flush=True)
    for char in prompt:
        print(char, end="", flush=True)
        await asyncio.sleep(random.uniform(0.01, 0.05))
    print("\"", end="", flush=True)
    await asyncio.sleep(0.5)
    print("\n\n[Gemini CLI] Analyzing request...", end="", flush=True)
    await asyncio.sleep(1.5)
    print(" Done.", flush=True)
    print("[Gemini CLI] Generating Python code...", flush=True)
    await asyncio.sleep(1.0)
    
    print("-" * 60)
    lines = code_output.split('\n')
    for line in lines:
        print(line)
        await asyncio.sleep(0.05) # Fast scroll effect
    print("-" * 60)
    print("\n[Gemini CLI] Code generation complete. Copied to clipboard.")

async def inject_coaching_reply(page):
    """Injects the pre-seeded coaching reply into the chat."""
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
        const selectors = ['.messages-container', '.chat-messages', 'main .overflow-y-auto', '.flex-1.overflow-y-auto'];
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

async def run_hackathon_demo():
    print("====================================================")
    print("   TRADEMIND AI - BINANCE HACKATHON DEMO DIRECTOR   ")
    print("====================================================")
    print("1. Ensure OpenClaw is running at: http://127.0.0.1:18789")
    print("2. Position this terminal (LEFT) and Browser (RIGHT).")
    print("3. Start Recording.")
    print("4. Automation starts in 5 seconds...")
    print("====================================================")
    
    await asyncio.sleep(5)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=50)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        # [0:00–0:30] Intro
        print("\n[0:00–0:30] PHASE 1: INTRO (User speaks over B-roll).")
        print(">> 'Did you know that up to 80% of retail traders lose money...?'")
        await asyncio.sleep(5) # Short wait, user edits this part usually

        # [0:30–1:00] OpenClaw Dashboard Overview
        print("\n[0:30–1:00] PHASE 2: DASHBOARD (Navigating to OpenClaw...)")
        try:
            await page.goto(OPENCLAW_URL)
            await asyncio.sleep(2)
            
            # Auto-configure Gateway if needed
            if await page.locator("input[placeholder*='ws://']").is_visible():
                if not GATEWAY_TOKEN:
                    raise RuntimeError("DEMO_GATEWAY_TOKEN is required when the local OpenClaw gateway asks for authentication.")
                print(">> Configuring Gateway...")
                await page.fill("input[placeholder*='ws://']", GATEWAY_WS_URL)
                await page.fill("input[type='password']", GATEWAY_TOKEN)
                await page.keyboard.press("Enter")
                await asyncio.sleep(3)

            print(">> Scrolling Dashboard...")
            await human_scroll(page, pixels=500)
        except Exception as e:
            print(f"Skipping dashboard interaction: {e}")

        # [1:00–1:30] Create Agent
        print("\n[1:00–1:30] PHASE 3: CREATE AGENT (TradeMind AI)")
        print(">> Creating agent...")
        try:
            await page.goto(f"{OPENCLAW_URL}/agents") 
            await asyncio.sleep(2)
            # Try to find a create button, generic fallbacks
            create_btns = ["button:has-text('Create Agent')", "button:has-text('New Agent')", ".btn-create"]
            for btn in create_btns:
                if await page.locator(btn).is_visible():
                    await page.click(btn)
                    break
            
            await asyncio.sleep(1)
            await human_type(page, "input[placeholder*='Name']", "TradeMind AI")
            await human_type(page, "textarea[placeholder*='Description'], textarea[placeholder*='Mission']", "A compassionate trading coach that analyzes emotional patterns on Binance.")
            await asyncio.sleep(2)
            # Just visually show it, maybe click save
            if await page.locator("button:has-text('Save')").is_visible():
                await page.click("button:has-text('Save')")
        except Exception:
            print(">> Could not find Agent creation UI, moving on...")

        # [1:30–2:15] Install Binance Skill
        print("\n[1:30–2:15] PHASE 4: BINANCE SKILL (Visuals)")
        print(">> Navigating to Skills...")
        try:
            await page.goto(f"{OPENCLAW_URL}/skills")
            await asyncio.sleep(2)
            # Mock search
            search_box = "input[placeholder*='Search']"
            if await page.locator(search_box).is_visible():
                await human_type(page, search_box, "Binance")
                await asyncio.sleep(2)
                
            # Click a 'Configure' or 'Install' if visible (Generic)
            # For video, just showing the screen is often enough
        except Exception:
            pass

        # [2:15–3:15] Create Custom Pattern Detector with Gemini CLI
        print("\n[2:15–3:15] PHASE 5: GEMINI CLI (Look at this terminal!)")
        
        # 1. Simulate Terminal Command
        prompt_text = "Write a Python function called analyze_patterns(trades)..."
        code_result = """import pandas as pd

def analyze_patterns(trades):
    # Calculate 10-period SMA
    df = pd.DataFrame(trades)
    df['ma10'] = df['price'].rolling(window=10).mean()
    
    # Identify FOMO (> 2% above MA) and Panic (< 2% below MA)
    fomo = df[(df['isBuyer']) & (df['price'] > 1.02 * df['ma10'])]
    panic = df[(~df['isBuyer']) & (df['price'] < 0.98 * df['ma10'])]
    
    return {
        "fomo_count": len(fomo),
        "panic_count": len(panic),
        "recommendation": "Pause trading." if len(fomo) > 3 else "Continue."
    }"""
        
        await simulate_gemini_cli(prompt_text, code_result)
        
        # 2. Paste into Browser
        print(">> Pasting code into OpenClaw Skill Editor...")
        try:
            # Assume we are creating a new skill
            await page.goto(f"{OPENCLAW_URL}/skills/new") # Hypothetical URL
            await asyncio.sleep(2)
            await human_type(page, "input[placeholder*='Name']", "Pattern Detector")
            
            # Find editor (monaco or textarea)
            editor = ".monaco-editor, textarea, [contenteditable='true']"
            if await page.locator(editor).first.is_visible():
                await page.click(editor)
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Backspace")
                # Simulate paste
                await page.evaluate(f"navigator.clipboard.writeText(`{code_result}`)")
                await page.keyboard.press("Control+V")
                await asyncio.sleep(3)
        except Exception:
            pass

        # [3:15–4:00] Build Workflow
        print("\n[3:15–4:00] PHASE 6: WORKFLOW (Visuals)")
        try:
            await page.goto(f"{OPENCLAW_URL}/workflows")
            await asyncio.sleep(3)
            # Pause for user to point mouse at things
        except Exception:
            pass

        # [4:00–4:45] Deploy to Telegram & Test
        print("\n[4:00–4:45] PHASE 7: CHAT TEST (The Finale)")
        print(">> Navigating to Chat...")
        await page.goto(OPENCLAW_CHAT_URL)
        await asyncio.sleep(4)
        
        print(">> Sending Prompt...")
        chat_input = "textarea, input[placeholder*='Type'], .chat-input"
        await human_type(page, chat_input, "Analyze my BTC trades for FOMO patterns.")
        await page.keyboard.press("Enter")
        
        print(">> Thinking...")
        await asyncio.sleep(4)
        
        print(">> Injecting Response...")
        success = await inject_coaching_reply(page)
        if success:
            print(">> INJECTION SUCCESSFUL.")
        else:
            print(">> INJECTION FAILED (Check Debug).")

        # [4:45–5:00] Closing Pitch
        print("\n[4:45–5:00] PHASE 8: CLOSING (Hold screen for overlay)")
        await asyncio.sleep(20)

        await browser.close()
        print("\n[FINISH] Demo Driver Complete.")

if __name__ == "__main__":
    asyncio.run(run_hackathon_demo())
