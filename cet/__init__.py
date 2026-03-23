from __future__ import annotations
"""claude-engineer-toolkit — Claude-powered CLI tools for backend engineers."""

__version__ = "0.1.0"
__author__ = "Your Name"

from cet.client import ClaudeClient

def tool(name: str, description: str = ""):
    """Decorator to register a custom cet plugin tool."""
    def decorator(fn):
        fn._cet_tool = True
        fn._cet_name = name
        fn._cet_description = description
        return fn
    return decorator

__all__ = ["ClaudeClient", "tool", "__version__"]
