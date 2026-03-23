from __future__ import annotations
"""
Disk-based response cache using diskcache.
"""

import diskcache
from pathlib import Path
from typing import Optional, Optional
from rich.console import Console
from rich.table import Table

console = Console()
CACHE_DIR = Path.home() / ".cet" / "cache"


class CacheManager:
    def __init__(self) -> None:
        self._cache = diskcache.Cache(str(CACHE_DIR))

    def get(self, key: str) -> Optional[str]:
        return self._cache.get(key)

    def set(self, key: str, value: str, ttl: int = 3600) -> None:
        self._cache.set(key, value, expire=ttl)

    def clear(self, tool: Optional[str] = None) -> None:
        if tool:
            keys_to_delete = [k for k in self._cache if str(k).startswith(f"{tool}:")]
            for k in keys_to_delete:
                del self._cache[k]
        else:
            self._cache.clear()

    def print_status(self) -> None:
        table = Table(title="CET Cache Status")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Cache directory", str(CACHE_DIR))
        table.add_row("Entries", str(len(self._cache)))
        table.add_row("Size on disk", self._human_size(self._cache.volume()))
        console.print(table)

    @staticmethod
    def _human_size(size: int) -> str:
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size //= 1024
        return f"{size:.1f} TB"


cache_manager = CacheManager()
