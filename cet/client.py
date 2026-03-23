from __future__ import annotations
"""
Claude API client wrapper with caching and chunking support.
"""

import hashlib
import json
from typing import Optional, Any

import anthropic
from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live

from cet.config import Config
from cet.cache import cache_manager

console = Console()


class ClaudeClient:
    """Thin wrapper around the Anthropic client with caching and progress display."""

    def __init__(self, config: Config):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.api_key)

    def ask(
        self,
        system: str,
        user: str,
        tool_name: str = "generic",
        use_cache: bool = True,
        stream: bool = True,
    ) -> str:
        """Send a prompt to Claude and return the response text."""

        from cet.mock import get_mock_response; return get_mock_response(tool_name) # MOCK
        cache_key = self._make_cache_key(tool_name, system, user)

        if use_cache and self.config.cache_enabled:
            cached = cache_manager.get(cache_key)
            if cached:
                console.print("[dim]✓ Using cached response[/dim]")
                return cached

        result = self._call_api(system=system, user=user, stream=stream)

        if use_cache and self.config.cache_enabled:
            cache_manager.set(cache_key, result, ttl=self.config.cache_ttl)

        return result

    def _call_api(self, system: str, user: str, stream: bool) -> str:
        """Make the actual API call."""
        if stream:
            return self._stream_response(system, user)
        else:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return response.content[0].text

    def _stream_response(self, system: str, user: str) -> str:
        """Stream response with live display."""
        collected = []
        with self.client.messages.stream(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        ) as stream:
            for text in stream.text_stream:
                collected.append(text)
                print(text, end="", flush=True)
        print()  # newline after streaming
        return "".join(collected)

    def _make_cache_key(self, tool_name: str, system: str, user: str) -> str:
        content = json.dumps({"tool": tool_name, "system": system, "user": user}, sort_keys=True)
        return f"{tool_name}:{hashlib.sha256(content.encode()).hexdigest()[:16]}"

def ask_mock(tool_name: str) -> str:
    from cet.mock import get_mock_response
    return get_mock_response(tool_name)
