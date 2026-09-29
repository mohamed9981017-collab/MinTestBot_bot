"""Configuration loading for the job hunter bot."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

DEFAULT_API_BASE = "https://api.telegram.org"


def split_list(value: str | None) -> list[str]:
    """Split a comma or newline separated string into a clean list."""
    if not value:
        return []
    items = []
    for chunk in value.replace("\n", ",").split(","):
        chunk = chunk.strip()
        if chunk:
            items.append(chunk)
    return items


def load_feeds_file(path: str) -> list[str]:
    """Read feed URLs from a file, one per line. Blank lines and ``#`` comments are skipped."""
    feeds = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line and not line.startswith("#"):
                feeds.append(line)
    return feeds


@dataclass
class Config:
    telegram_token: str
    telegram_chat_id: str
    feeds: list[str] = field(default_factory=list)
    include_keywords: list[str] = field(default_factory=list)
    exclude_keywords: list[str] = field(default_factory=list)
    state_file: str = "seen_jobs.json"
    poll_interval: int = 900
    max_items_per_run: int = 20
    request_timeout: int = 20
    dry_run: bool = False
    api_base: str = DEFAULT_API_BASE

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> "Config":
        env = dict(os.environ if env is None else env)

        token = (env.get("TELEGRAM_TOKEN") or "").strip()
        chat_id = (env.get("TELEGRAM_CHAT_ID") or "").strip()
        if not token:
            raise ValueError("TELEGRAM_TOKEN is not set")
        if not chat_id:
            raise ValueError("TELEGRAM_CHAT_ID is not set")

        feeds = split_list(env.get("RSS_FEEDS"))
        feeds_file = (env.get("RSS_FEEDS_FILE") or "").strip()
        if not feeds and feeds_file and os.path.exists(feeds_file):
            feeds = load_feeds_file(feeds_file)

        return cls(
            telegram_token=token,
            telegram_chat_id=chat_id,
            feeds=feeds,
            include_keywords=split_list(env.get("JOB_KEYWORDS")),
            exclude_keywords=split_list(env.get("EXCLUDE_KEYWORDS")),
            state_file=(env.get("STATE_FILE") or "seen_jobs.json").strip(),
            poll_interval=int(env.get("POLL_INTERVAL") or 900),
            max_items_per_run=int(env.get("MAX_ITEMS_PER_RUN") or 20),
            request_timeout=int(env.get("REQUEST_TIMEOUT") or 20),
            dry_run=str(env.get("DRY_RUN") or "").strip().lower() in {"1", "true", "yes"},
            api_base=(env.get("TELEGRAM_API_BASE") or DEFAULT_API_BASE).rstrip("/"),
        )
