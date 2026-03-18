from __future__ import annotations

import httpx
import os
import asyncio
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class TelegramBotService:
    """Service to send and receive behavioral alerts and trade summaries."""
    
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else None
        self._offset = 0

    async def send_message(self, text: str, chat_id: Optional[str] = None) -> bool:
        """Send a message to the configured chat_id or a specific one."""
        target_id = chat_id or self.chat_id
        if not self.base_url or not target_id:
            return False
            
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": target_id,
                "text": text,
                "parse_mode": "HTML"
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=10)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Telegram send error: {e}")
            return False

    async def get_updates(self) -> List[Dict[str, Any]]:
        """Fetch new messages from Telegram."""
        if not self.base_url:
            return []
            
        try:
            url = f"{self.base_url}/getUpdates"
            params = {"offset": self._offset, "timeout": 30}
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=35)
                if response.status_code != 200:
                    return []
                
                data = response.json()
                updates = data.get("result", [])
                if updates:
                    self._offset = updates[-1]["update_id"] + 1
                return updates
        except Exception as e:
            logger.error(f"Telegram poll error: {e}")
            return []

    async def set_commands(self, commands: List[Dict[str, str]]) -> bool:
        """Register the list of available commands with Telegram UI."""
        if not self.base_url:
            return False
        try:
            url = f"{self.base_url}/setMyCommands"
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json={"commands": commands}, timeout=10)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Telegram setCommands error: {e}")
            return False

    def is_configured(self) -> bool:
        return bool(self.token and self.chat_id)
