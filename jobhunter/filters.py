"""Keyword filtering for job entries."""

from __future__ import annotations

import re

from .feeds import JobEntry


def _compile(keyword: str) -> re.Pattern[str] | None:
    keyword = keyword.strip()
    if not keyword:
        return None
    escaped = re.escape(keyword)
    prefix = r"\b" if re.match(r"\w", keyword[0]) else ""
    suffix = r"\b" if re.match(r"\w", keyword[-1]) else ""
    return re.compile(prefix + escaped + suffix, re.IGNORECASE)


def compile_keywords(keywords: list[str]) -> list[re.Pattern[str]]:
    patterns = []
    for keyword in keywords:
        pattern = _compile(keyword)
        if pattern is not None:
            patterns.append(pattern)
    return patterns


def text_of(entry: JobEntry) -> str:
    return " ".join(part for part in (entry.title, entry.summary, entry.source) if part)


def matches(
    entry: JobEntry,
    include: list[re.Pattern[str]],
    exclude: list[re.Pattern[str]],
) -> bool:
    """Return True when the entry passes the exclude filter and matches any include keyword."""
    text = text_of(entry)
    if exclude and any(pattern.search(text) for pattern in exclude):
        return False
    if not include:
        return True
    return any(pattern.search(text) for pattern in include)
