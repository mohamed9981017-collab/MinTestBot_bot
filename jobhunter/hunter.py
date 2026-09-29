"""Polling pipeline: fetch feeds, filter, dedupe, deliver."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from . import feeds as feeds_module
from . import formatting, telegram
from .config import Config
from .filters import compile_keywords, matches
from .store import SeenStore

logger = logging.getLogger(__name__)


@dataclass
class RunResult:
    feeds_ok: int = 0
    feeds_failed: int = 0
    entries: int = 0
    matched: int = 0
    new: int = 0
    sent: int = 0

    def __str__(self) -> str:
        return (
            f"feeds_ok={self.feeds_ok} feeds_failed={self.feeds_failed} "
            f"entries={self.entries} matched={self.matched} new={self.new} sent={self.sent}"
        )


def collect_entries(config: Config, session=None) -> tuple[list, int, int]:
    entries = []
    ok = failed = 0
    for url in config.feeds:
        try:
            entries.extend(
                feeds_module.fetch_feed(url, timeout=config.request_timeout, session=session)
            )
            ok += 1
        except Exception as exc:  # a single broken feed must not stop the cycle
            failed += 1
            logger.warning("failed to fetch %s: %s", url, exc)
    return entries, ok, failed


def run_once(config: Config, session=None) -> RunResult:
    result = RunResult()

    entries, ok, failed = collect_entries(config, session=session)
    result.feeds_ok = ok
    result.feeds_failed = failed
    result.entries = len(entries)

    include = compile_keywords(config.include_keywords)
    exclude = compile_keywords(config.exclude_keywords)
    matched = [entry for entry in entries if matches(entry, include, exclude)]
    result.matched = len(matched)

    store = SeenStore(config.state_file)
    fresh = [entry for entry in matched if not store.is_seen(entry.uid)]
    result.new = len(fresh)

    for entry in fresh[: config.max_items_per_run]:
        if config.dry_run:
            logger.info("[dry-run] %s -> %s", entry.source, entry.title)
            result.sent += 1
            continue
        telegram.send_message(
            config.telegram_token,
            config.telegram_chat_id,
            formatting.format_job(entry),
            api_base=config.api_base,
            timeout=config.request_timeout,
            session=session,
        )
        store.add(entry.uid)
        result.sent += 1

    if not config.dry_run and result.sent:
        store.save()

    return result
