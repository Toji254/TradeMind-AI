from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
import os


load_dotenv()


class Settings(BaseModel):
    app_name: str = "TradeMind AI"
    env: str = os.getenv("TRADEMIND_ENV", "development")
    db_path: Path = Path(os.getenv("TRADEMIND_DB_PATH", "./data/trademind.db"))
    binance_api_key: str | None = os.getenv("BINANCE_API_KEY")
    binance_api_secret: str | None = os.getenv("BINANCE_API_SECRET")


settings = Settings()
