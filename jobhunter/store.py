"""Persistent record of jobs already delivered, to avoid duplicate posts."""

from __future__ import annotations

import json
import os
from pathlib import Path


class SeenStore:
    def __init__(self, path: str | os.PathLike[str]):
        self.path = Path(path)
        self._seen: set[str] = self._load()

    def _load(self) -> set[str]:
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (FileNotFoundError, json.JSONDecodeError):
            return set()
        if isinstance(data, dict):
            data = data.get("seen", [])
        return set(data or [])

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        with tmp.open("w", encoding="utf-8") as handle:
            json.dump({"seen": sorted(self._seen)}, handle, indent=2)
        os.replace(tmp, self.path)

    def is_seen(self, key: str) -> bool:
        return key in self._seen

    def add(self, key: str) -> None:
        self._seen.add(key)

    def __len__(self) -> int:
        return len(self._seen)
