from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.app.config import settings
from src.app.services import TradeMindService
from src.storage.local_db import add_journal_entry, list_symbols

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="TradeMind AI")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
service = TradeMindService()


@app.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    symbol: str | None = None,
    limit: int = 100,
    market: str = "spot",
    status: str | None = None,
) -> HTMLResponse:
    summary = service.analyze_local(symbol=symbol, limit=limit)
    context = {
        "request": request,
        "summary": summary,
        "symbols": list_symbols(settings.db_path),
        "symbol": symbol,
        "market": market,
        "limit": limit,
        "status": status,
    }
    return templates.TemplateResponse(request, "dashboard.html", context)


@app.post("/sync")
def sync(symbol: str = Form(...), limit: int = Form(100), market: str = Form("spot")) -> RedirectResponse:
    inserted = service.sync_symbol(symbol=symbol, limit=limit, market=market)
    return RedirectResponse(url=f"/?symbol={symbol.upper()}&market={market}&limit={limit}&status=Synced+{inserted}+{market}+trades", status_code=303)


@app.post("/journal")
def journal(tag: str = Form("general"), text: str = Form(...), symbol: str = Form(""), market: str = Form("spot"), limit: int = Form(100)) -> RedirectResponse:
    add_journal_entry(settings.db_path, tag=tag, text=text)
    query = f"/?market={market}&limit={limit}&status=Journal+entry+saved"
    if symbol:
        query = f"/?symbol={symbol.upper()}&market={market}&limit={limit}&status=Journal+entry+saved"
    return RedirectResponse(url=query, status_code=303)
