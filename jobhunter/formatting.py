"""Render job entries as Telegram HTML messages."""

from __future__ import annotations

import html

from .feeds import JobEntry

MAX_MESSAGE_LENGTH = 4096
MAX_SUMMARY_LENGTH = 600


def escape(text: str) -> str:
    return html.escape(text or "", quote=False)


def truncate(text: str, limit: int) -> str:
    text = text or ""
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "\u2026"


def format_job(entry: JobEntry) -> str:
    lines = [f"\U0001f4bc <b>{escape(entry.title)}</b>"]
    if entry.published:
        lines.append(f"\U0001f5d3 {escape(entry.published)}")
    if entry.summary:
        lines.append("")
        lines.append(escape(truncate(entry.summary, MAX_SUMMARY_LENGTH)))
    if entry.link:
        lines.append("")
        href = html.escape(entry.link, quote=True)
        lines.append(f'\U0001f517 <a href="{href}">Read more / apply</a>')
    return truncate("\n".join(lines), MAX_MESSAGE_LENGTH)
