from __future__ import annotations
"""
cet - Claude Engineer Toolkit
Main CLI entry point.
"""
import typer
from rich.console import Console
from rich import print as rprint

from cet.tools.explain import explain_tool
from cet.tools.pr_review import pr_tool
from cet.tools.test_gen import test_tool
from cet.tools.spec_gen import spec_tool
from cet.cache import cache_manager
from cet import __version__

app = typer.Typer(
    name="cet",
    help="🛠️  Claude Engineer Toolkit — AI-powered tools for backend engineers.",
    add_completion=True,
    rich_markup_mode="rich",
)

console = Console()


def version_callback(value: bool) -> None:
    if value:
        rprint(f"[bold cyan]cet[/bold cyan] version [bold]{__version__}[/bold]")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """🛠️  Claude Engineer Toolkit"""
    pass


@app.command()
def explain(
    file: str = typer.Argument(..., help="File or directory to explain"),
    focus: str = typer.Option(None, "--focus", "-f", help="Focus area: security, performance, logic"),
    format: str = typer.Option("terminal", "--format", help="Output format: terminal, markdown, json"),
    output: str = typer.Option(None, "--output", "-o", help="Write output to file"),
    mock: bool = typer.Option(False, "--mock", help="Use mock response, no API call"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Skip cache lookup"),
) -> None:
    """
    [bold]Explain any code file in plain English.[/bold]

    Examples:
      cet explain legacy_auth.php
      cet explain src/auth/jwt.go --focus security
      cet explain query.sql --format markdown > explanation.md
    """
    explain_tool(file=file, focus=focus, fmt=format, output=output, no_cache=no_cache, mock=mock)


@app.command()
def pr(
    branch: str = typer.Option(None, "--branch", "-b", help="Compare against this branch (default: staged changes)"),
    file: str = typer.Option(None, "--file", help="Path to a .diff file"),
    focus: str = typer.Option(None, "--focus", "-f", help="Focus area: security, performance, style"),
    output: str = typer.Option("terminal", "--output", "-o", help="Output format: terminal, github-comment, markdown"),
    mock: bool = typer.Option(False, "--mock", help="Use mock response, no API call"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Skip cache lookup"),
) -> None:
    """
    [bold]Review a pull request or staged changes like a senior engineer.[/bold]

    Examples:
      cet pr                          # review staged changes
      cet pr --branch main            # compare to main
      cet pr --focus security         # security-focused review
      cet pr --output github-comment  # format for GitHub PR comment
    """
    pr_tool(branch=branch, diff_file=file, focus=focus, output=output, no_cache=no_cache, mock=mock)


@app.command()
def test(
    file: str = typer.Argument(..., help="Python file to generate tests for"),
    framework: str = typer.Option("pytest", "--framework", help="Test framework: pytest, unittest"),
    output: str = typer.Option(None, "--output", "-o", help="Write test file to this path"),
    coverage_focus: str = typer.Option(None, "--coverage-focus", help="Focus: edge-cases, happy-path, security"),
    mock: bool = typer.Option(False, "--mock", help="Use mock response, no API call"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Skip cache lookup"),
) -> None:
    """
    [bold]Generate test scaffolds for any Python file.[/bold]

    Examples:
      cet test src/services/user_service.py
      cet test src/api/payments.py --coverage-focus edge-cases
      cet test src/utils.py --output tests/test_utils.py
    """
    test_tool(file=file, framework=framework, output=output, coverage_focus=coverage_focus, no_cache=no_cache)


@app.command()
def spec(
    path: str = typer.Argument(..., help="File or directory containing routes/controllers"),
    framework: str = typer.Option(None, "--framework", help="Framework hint: fastapi, flask, django"),
    output: str = typer.Option(None, "--output", "-o", help="Write spec to this file (default: stdout)"),
    format: str = typer.Option("yaml", "--format", help="Output format: yaml, json"),
    mock: bool = typer.Option(False, "--mock", help="Use mock response, no API call"),
    no_cache: bool = typer.Option(False, "--no-cache", help="Skip cache lookup"),
) -> None:
    """
    [bold]Generate an OpenAPI 3.1 spec from your routes and controllers.[/bold]

    Examples:
      cet spec src/routes/
      cet spec src/api/users.py --output openapi.yaml
      cet spec . --framework fastapi --format json
    """
    spec_tool(path=path, framework=framework, output=output, fmt=format, no_cache=no_cache, mock=mock)


@app.command()
def cache(
    status: bool = typer.Option(False, "--status", help="Show cache stats"),
    clear: bool = typer.Option(False, "--clear", help="Clear cache"),
    tool: str = typer.Option(None, "--tool", "-t", help="Limit to a specific tool"),
) -> None:
    """
    [bold]Manage the local response cache.[/bold]

    Examples:
      cet cache --status
      cet cache --clear
      cet cache --clear --tool pr
    """
    if status:
        cache_manager.print_status()
    elif clear:
        cache_manager.clear(tool=tool)
        console.print(f"[green]✓ Cache cleared{f' for tool: {tool}' if tool else ''}[/green]")
    else:
        console.print("[yellow]Use --status or --clear[/yellow]")


if __name__ == "__main__":
    app()
