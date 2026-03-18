from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.app.config import settings
from src.app.services import TradeMindService
from src.storage.local_db import list_symbols_by_market, add_journal_entry

app = FastAPI(title="TradeMind AI - V2")
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

service = TradeMindService()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, market: str = "spot", symbol: str | None = None, status: str | None = None):
    # Fetch symbols for the market
    symbols = list_symbols_by_market(settings.db_path, market=market)
    
    # If no symbol selected, pick the first one if available
    selected_symbol = symbol if symbol and symbol in symbols else (symbols[0] if symbols else None)
    
    # Fetch account snapshot
    account_snapshot = {}
    try:
        account_snapshot = service.get_account_snapshot(market=market)
    except Exception as e:
        account_snapshot = {"error": str(e)}

    # Fetch analysis if symbol exists
    analysis = None
    if selected_symbol:
        try:
            analysis = service.analyze_local(symbol=selected_symbol)
        except Exception as e:
            analysis = {"error": str(e), "market_context": {"fear_greed": {"value": 50, "classification": "Neutral"}}}

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "market": market,
            "symbols": symbols,
            "selected_symbol": selected_symbol,
            "account": account_snapshot,
            "analysis": analysis,
            "env": settings.env,
            "status": status,
        },
    )

@app.post("/sync")
async def sync(symbol: str = Form(...), limit: int = Form(100), market: str = Form("spot")):
    try:
        inserted = service.sync_symbol(symbol=symbol, limit=limit, market=market)
        return RedirectResponse(url=f"/?symbol={symbol.upper()}&market={market}&status=Synced {inserted} trades", status_code=303)
    except Exception as e:
        # Graceful fallback for demo - show error in status message
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            error_msg = "API key invalid (demo mode - using placeholder credentials)"
        return RedirectResponse(url=f"/?symbol={symbol.upper()}&market={market}&status=Sync failed: {error_msg}", status_code=303)

@app.post("/journal")
async def journal(tag: str = Form("general"), text: str = Form(...), symbol: str = Form(""), market: str = Form("spot")):
    add_journal_entry(settings.db_path, tag=tag, text=text)
    url = f"/?market={market}&status=Journal entry saved"
    if symbol:
        url += f"&symbol={symbol}"
    return RedirectResponse(url=url, status_code=303)

@app.get("/logs", response_class=HTMLResponse)
async def logs(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})

@app.get("/api/analysis/{symbol}", response_model=dict)
async def get_analysis(symbol: str):
    return service.analyze_local(symbol=symbol)
