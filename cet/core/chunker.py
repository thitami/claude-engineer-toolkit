from __future__ import annotations
"""
File chunking utilities for large codebases.
Splits files into Claude-friendly chunks while preserving context.
"""

from pathlib import Path
from typing import Iterator

MAX_CHUNK_CHARS = 80_000  # ~20k tokens, safe for claude-sonnet


def read_file(path: str) -> str:
    """Read a file and return its content."""
    return Path(path).read_text(encoding="utf-8", errors="replace")


def chunk_text(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    """Split text into chunks, trying to break at logical boundaries."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_chars:
            chunks.append(text)
            break
        split_at = text.rfind("\n\n", 0, max_chars)
        if split_at == -1:
            split_at = text.rfind("\n", 0, max_chars)
        if split_at == -1:
            split_at = max_chars
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()

    return chunks


def collect_files(path: str, extensions: Optional[List[str]] = None) -> list[Path]:
    """Collect all files from a path (file or directory)."""
    p = Path(path)
    if p.is_file():
        return [p]
    
    files = []
    for f in sorted(p.rglob("*")):
        if f.is_file() and not any(part.startswith(".") for part in f.parts):
            if extensions is None or f.suffix in extensions:
                files.append(f)
    return files
