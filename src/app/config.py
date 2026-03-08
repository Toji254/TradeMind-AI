from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()


class Settings(BaseModel):
    app_name: str = "TradeMind AI"
    env: str = os.getenv("TRADEMIND_ENV", "development")
    db_path: Path = Path(os.getenv("TRADEMIND_DB_PATH", "./data/trademind.db"))

    binance_spot_api_key: str | None = os.getenv("BINANCE_SPOT_API_KEY")
    binance_spot_api_secret: str | None = os.getenv("BINANCE_SPOT_API_SECRET")
    binance_futures_api_key: str | None = os.getenv("BINANCE_FUTURES_API_KEY")
    binance_futures_api_secret: str | None = os.getenv("BINANCE_FUTURES_API_SECRET")

    binance_spot_base_url: str = os.getenv("BINANCE_SPOT_BASE_URL", "https://testnet.binance.vision")
    binance_futures_base_url: str = os.getenv("BINANCE_FUTURES_BASE_URL", "https://testnet.binancefuture.com")


settings = Settings()
