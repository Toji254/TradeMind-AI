import asyncio
import os
import subprocess
import time
import socket
from playwright.async_api import async_playwright

def wait_for_port(port, host='127.0.0.1', timeout=15):
    """Wait for a port to become active."""
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(1)
            if time.time() - start_time > timeout:
                return False

async def run_showcase():
    # 1. Start the TradeMind AI server in the background
    print("Starting TradeMind AI server...")
    # Use a log file for server output to avoid blocking
    with open("walkthrough/server.log", "w") as log:
        server_process = subprocess.Popen(
            [".venv/Scripts/python.exe", "-m", "src.app.cli", "serve-web"],
            cwd=os.getcwd(),
            stdout=log,
            stderr=log
        )
    
    # Wait for server to warm up properly
    print("Waiting for server to be ready on port 8000...")
    if not wait_for_port(8000):
        print("Error: Server failed to start on port 8000 within timeout.")
        server_process.terminate()
        return
    
    print("Server ready. Starting browser walkthrough...")
    async with async_playwright() as p:
        print("Launching browser for walkthrough...")
        browser = await p.chromium.launch(headless=True)
        # Create a context with video recording enabled
        context = await browser.new_context(
            record_video_dir="walkthrough/video/",
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        
        # Step 1: Dashboard Overview
        print("Capturing Dashboard Overview...")
        await page.goto("http://127.0.0.1:8000")
        await asyncio.sleep(3) # Wait for market intelligence to load
        await page.screenshot(path="walkthrough/01_dashboard_overview.png")
        
        # Step 2: Market Intelligence Highlight
        print("Highlighting Real-time Intelligence...")
        await page.locator("#market-intel").scroll_into_view_if_needed()
        await page.screenshot(path="walkthrough/02_market_intelligence.png")
        
        # Step 3: Trading Journal Entry
        print("Demonstrating Journal Entry...")
        await page.select_option("select[name='tag']", "pretrade")
        await page.fill("textarea[name='text']", "Walking through the new TradeMind AI updates. Feeling confident about the behavioral insights!")
        await page.screenshot(path="walkthrough/03_journal_before_submit.png")
        await page.click("button:has-text('Save Entry')")
        await asyncio.sleep(2)
        await page.screenshot(path="walkthrough/04_journal_saved.png")
        
        # Step 4: Behavioral Analysis & Discipline Score
        print("Reviewing Discipline Analysis...")
        await page.locator("#analysis-card").scroll_into_view_if_needed()
        await page.screenshot(path="walkthrough/05_behavioral_analysis.png")
        
        # Step 5: Switch to Futures
        print("Switching to Futures Market...")
        await page.click("a:has-text('Futures')")
        await asyncio.sleep(3)
        await page.screenshot(path="walkthrough/06_futures_market.png")
        
        await browser.close()
        print("Walkthrough complete. Visuals saved to 'walkthrough/' folder.")
        
    # Stop the server
    server_process.terminate()

if __name__ == "__main__":
    if not os.path.exists("walkthrough"):
        os.makedirs("walkthrough")
    asyncio.run(run_showcase())
