"""Minimal Telegram Bot API client."""

from __future__ import annotations

import requests

from .config import DEFAULT_API_BASE


class TelegramError(RuntimeError):
    """Raised when the Telegram API rejects a request."""


def send_message(
    token: str,
    chat_id: str,
    text: str,
    api_base: str = DEFAULT_API_BASE,
    disable_web_page_preview: bool = True,
    timeout: int = 20,
    session=None,
) -> dict:
    """Send an HTML message and return the Telegram ``result`` payload."""
    session = session or requests
    url = f"{api_base.rstrip('/')}/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": disable_web_page_preview,
    }
    response = session.post(url, json=payload, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise TelegramError(f"Telegram API error: {data.get('description', data)}")
    return data["result"]
