from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.app.config import settings
from src.app.services import TradeMindService
from src.connectors.binance_client import BinanceCredentials
from src.storage.local_db import add_journal_entry, list_symbols

# Import transit from bot_runner (will be empty if bot not running)
try:
    from src.app.bot_runner import KEY_TRANSIT
except ImportError:
    KEY_TRANSIT = {}

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
    
    # Check if keys are in cookies
    has_spot_keys = "api_key" in request.cookies and "api_secret" in request.cookies
    has_futures_keys = "futures_api_key" in request.cookies and "futures_api_secret" in request.cookies
    
    context = {
        "request": request,
        "summary": summary,
        "symbols": list_symbols(settings.db_path),
        "symbol": symbol,
        "market": market,
        "limit": limit,
        "status": status,
        "has_keys": has_spot_keys or has_futures_keys,
        "has_spot_keys": has_spot_keys,
        "has_futures_keys": has_futures_keys,
    }
    return templates.TemplateResponse(request, "dashboard.html", context)


@app.post("/config-keys")
def config_keys(
    market_type: str = Form("spot"),
    api_key: str = Form(...),
    api_secret: str = Form(...)
) -> RedirectResponse:
    response = RedirectResponse(url=f"/?status={market_type.title()}+API+Keys+connected+locally", status_code=303)
    
    if market_type == "spot":
        response.set_cookie(key="api_key", value=api_key, httponly=True)
        response.set_cookie(key="api_secret", value=api_secret, httponly=True)
    else:
        response.set_cookie(key="futures_api_key", value=api_key, httponly=True)
        response.set_cookie(key="futures_api_secret", value=api_secret, httponly=True)
        
    return response


@app.post("/clear-keys")
def clear_keys() -> RedirectResponse:
    response = RedirectResponse(url="/?status=All+API+Keys+cleared", status_code=303)
    response.delete_cookie("api_key")
    response.delete_cookie("api_secret")
    response.delete_cookie("futures_api_key")
    response.delete_cookie("futures_api_secret")
    return response


@app.post("/claim-telegram-keys")
def claim_telegram_keys(chat_id: str = Form(...)) -> RedirectResponse:
    try:
        cid = int(chat_id)
        if cid in KEY_TRANSIT:
            user_transit = KEY_TRANSIT.pop(cid)
            response = RedirectResponse(url="/?status=Keys+claimed+from+Telegram", status_code=303)
            
            # Handle Spot
            if "spot" in user_transit:
                response.set_cookie(key="api_key", value=user_transit["spot"]["api_key"], httponly=True)
                response.set_cookie(key="api_secret", value=user_transit["spot"]["api_secret"], httponly=True)
            
            # Handle Futures (Separate cookies)
            if "futures" in user_transit:
                response.set_cookie(key="futures_api_key", value=user_transit["futures"]["api_key"], httponly=True)
                response.set_cookie(key="futures_api_secret", value=user_transit["futures"]["api_secret"], httponly=True)
                
            return response
        else:
            return RedirectResponse(url="/?status=No+keys+found+for+this+Chat+ID", status_code=303)
    except ValueError:
        return RedirectResponse(url="/?status=Invalid+Chat+ID", status_code=303)


@app.post("/sync")
def sync(
    request: Request,
    symbol: str = Form(...),
    limit: int = Form(100),
    market: str = Form("spot")
) -> RedirectResponse:
    # Check for user-provided keys in cookies
    if market == "spot":
        user_api_key = request.cookies.get("api_key")
        user_api_secret = request.cookies.get("api_secret")
    else:
        user_api_key = request.cookies.get("futures_api_key")
        user_api_secret = request.cookies.get("futures_api_secret")
    
    credentials = None
    if user_api_key and user_api_secret:
        credentials = BinanceCredentials(
            api_key=user_api_key,
            api_secret=user_api_secret,
            base_url=settings.binance_spot_base_url if market == "spot" else settings.binance_futures_base_url
        )
    
    try:
        inserted = service.sync_symbol(symbol=symbol, limit=limit, market=market, credentials=credentials)
        return RedirectResponse(url=f"/?symbol={symbol.upper()}&market={market}&limit={limit}&status=Synced+{inserted}+{market}+trades", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/?status=Sync+Error:+{str(e)}", status_code=303)


@app.post("/journal")
def journal(tag: str = Form("general"), text: str = Form(...), symbol: str = Form(""), market: str = Form("spot"), limit: int = Form(100)) -> RedirectResponse:
    add_journal_entry(settings.db_path, tag=tag, text=text)
    query = f"/?market={market}&limit={limit}&status=Journal+entry+saved"
    if symbol:
        query = f"/?symbol={symbol.upper()}&market={market}&limit={limit}&status=Journal+entry+saved"
    return RedirectResponse(url=query, status_code=303)
