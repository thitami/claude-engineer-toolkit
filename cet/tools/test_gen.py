from __future__ import annotations
from typing import Optional, List
"""cet test — generate pytest scaffolds for any Python file."""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from cet.config import Config
from cet.client import ClaudeClient
from cet.core.chunker import read_file
from cet.prompts import test_gen as prompts

console = Console()


def test_tool(
    file: str,
    framework: str,
    output: Optional[str],
    coverage_focus: Optional[str],
    no_cache: bool,
) -> None:
    config = Config.load()
    client = ClaudeClient(config)
    path = Path(file)

    if not path.exists():
        console.print(f"[red]File not found: {file}[/red]")
        raise SystemExit(1)

    if path.suffix != ".py":
        console.print(f"[yellow]Warning: test generation works best with Python files[/yellow]")

    test_config = config.tools.get("test")
    effective_framework = framework or (test_config.framework if test_config else "pytest")
    effective_output = output or (test_config.output_dir if test_config else None)

    code = read_file(file)
    project_context = _build_project_context(config)

    console.print(Panel(
        f"[bold cyan]cet test[/bold cyan] · [dim]{file}[/dim]"
        + (f" · [yellow]{coverage_focus}[/yellow]" if coverage_focus else ""),
        expand=False,
    ))

    user_prompt = prompts.build_user_prompt(
        filename=path.name,
        code=code,
        framework=effective_framework,
        coverage_focus=coverage_focus,
        project_context=project_context,
    )

    result = client.ask(
        system=prompts.SYSTEM,
        user=user_prompt,
        tool_name="test",
        use_cache=not no_cache,
    )

    if effective_output:
        out_path = Path(effective_output)
        if out_path.is_dir():
            out_path = out_path / f"test_{path.stem}.py"
        out_path.write_text(result)
        console.print(f"\n[green]✓ Tests written to {out_path}[/green]")
    else:
        console.print(Syntax(result, "python", theme="monokai", line_numbers=True))


def _build_project_context(config: Config) -> str:
    parts = []
    if config.project_framework:
        parts.append(f"Framework: {config.project_framework}")
    return "\n".join(parts)
