from __future__ import annotations
from typing import Optional
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.live import Live
from rich import box

console = Console()

LANGUAGE_COLORS = {
    "python": "green",
    "php": "blue",
    "go": "cyan",
    "typescript": "blue",
    "javascript": "yellow",
    "ruby": "red",
    "java": "red",
    "rust": "yellow",
    "sql": "magenta",
    "bash": "green",
    "yaml": "cyan",
    "text": "white",
}

def print_header(tool: str, target: str, meta: dict = {}) -> None:
    """Print a rich header panel for any cet tool."""
    meta_parts = []
    for key, val in meta.items():
        if val:
            meta_parts.append(f"[dim]{key}:[/dim] [bold]{val}[/bold]")

    meta_str = "  ·  ".join(meta_parts)
    content = f"[bold cyan]cet {tool}[/bold cyan]  [dim]·[/dim]  [white]{target}[/white]"
    if meta_str:
        content += f"\n{meta_str}"

    console.print(Panel(content, expand=False, border_style="cyan", padding=(0, 1)))


def print_waiting(message: str = "Asking Claude...") -> Live:
    """Return a Live context with a spinner. Use as a context manager."""
    spinner = Spinner("dots", text=f" [dim]{message}[/dim]", style="cyan")
    return Live(spinner, console=console, refresh_per_second=10, transient=True)


def print_result(markdown_text: str, elapsed: Optional[float] = None) -> None:
    """Print the Claude response with a top rule and optional timing."""
    console.print()
    console.print(Rule(style="dim"))
    console.print(Markdown(markdown_text))
    console.print(Rule(style="dim"))
    if elapsed is not None:
        console.print(f"[dim]  ⏱  {elapsed:.1f}s[/dim]")
    console.print()


def print_success(message: str) -> None:
    console.print(f"\n[bold green]✓[/bold green] {message}")


def print_error(message: str) -> None:
    console.print(f"\n[bold red]✗[/bold red] {message}")


def print_warning(message: str) -> None:
    console.print(f"\n[yellow]⚠[/yellow]  {message}")


def file_meta(path: Path, language: str) -> dict:
    """Build metadata dict for the header panel."""
    size = path.stat().st_size
    size_str = f"{size:,} bytes" if size < 10_000 else f"{size // 1000}k"
    lang_color = LANGUAGE_COLORS.get(language, "white")
    return {
        "lang": f"[{lang_color}]{language}[/{lang_color}]",
        "size": size_str,
    }
