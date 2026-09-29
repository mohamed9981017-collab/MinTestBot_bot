"""Fetching and parsing RSS/Atom job feeds."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

import feedparser
import requests

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

USER_AGENT = "job-hunter-bot/0.1 (+https://github.com/mohamed9981017-collab/MinTestBot_bot)"


@dataclass
class JobEntry:
    title: str
    link: str
    summary: str
    published: str
    source: str
    uid: str


def clean_html(text: str) -> str:
    """Strip tags and collapse whitespace so feed HTML is safe to re-render."""
    if not text:
        return ""
    text = _TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return _WS_RE.sub(" ", text).strip()


def _entry_uid(entry: dict, source: str, link: str, title: str) -> str:
    for key in ("id", "guid"):
        value = entry.get(key)
        if value:
            return f"{source}:{value}"
    if link:
        return f"{source}:{link}"
    return f"{source}:{title}"


def parse_feed(content: bytes | str, source: str) -> list[JobEntry]:
    parsed = feedparser.parse(content)
    entries = []
    for raw in parsed.entries:
        title = clean_html(raw.get("title", "")) or "(untitled)"
        link = (raw.get("link") or "").strip()
        summary = clean_html(raw.get("summary") or raw.get("description") or "")
        published = (raw.get("published") or raw.get("updated") or "").strip()
        entries.append(
            JobEntry(
                title=title,
                link=link,
                summary=summary,
                published=published,
                source=source,
                uid=_entry_uid(raw, source, link, title),
            )
        )
    return entries


def fetch_feed(url: str, timeout: int = 20, session=None) -> list[JobEntry]:
    """Download and parse a single feed, raising on HTTP errors."""
    session = session or requests
    response = session.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    return parse_feed(response.content, source=url)
