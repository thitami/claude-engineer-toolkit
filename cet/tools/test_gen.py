from __future__ import annotations
from typing import Optional
"""cet test — generate pytest scaffolds for any Python file."""

import time
from pathlib import Path
from rich.syntax import Syntax
from rich.rule import Rule

from cet.core.chunker import read_file
from cet.core.ui import console, print_header, print_waiting, print_success, print_error, file_meta
from cet.prompts import test_gen as prompts


def test_tool(
    file: str,
    framework: str,
    output: Optional[str],
    coverage_focus: Optional[str],
    no_cache: bool,
    mock: bool = False,
) -> None:
    path = Path(file)

    if not path.exists():
        print_error(f"File not found: {file}")
        raise SystemExit(1)

    if path.suffix != ".py":
        console.print("[yellow]⚠[/yellow]  Test generation works best with Python files")

    meta = file_meta(path, "python")
    meta["framework"] = framework or "pytest"
    if coverage_focus:
        meta["focus"] = coverage_focus

    print_header("test", file, meta)

    if mock:
        from cet.mock import get_mock_response
        _print_tests(get_mock_response("test"), output, path)
        return

    from cet.config import Config
    from cet.client import ClaudeClient

    config = Config.load()
    test_config = config.tools.get("test")
    effective_framework = framework or (test_config.framework if test_config else "pytest")
    effective_output = output or (test_config.output_dir if test_config else None)

    code = read_file(file)
    project_context = f"Framework: {config.project_framework}" if config.project_framework else ""

    user_prompt = prompts.build_user_prompt(
        filename=path.name,
        code=code,
        framework=effective_framework,
        coverage_focus=coverage_focus,
        project_context=project_context,
    )

    client = ClaudeClient(config)
    start = time.time()
    with print_waiting(f"Generating {effective_framework} tests..."):
        result = client.ask(
            system=prompts.SYSTEM,
            user=user_prompt,
            tool_name="test",
            use_cache=not no_cache,
            stream=False,
        )
    elapsed = time.time() - start
    _print_tests(result, effective_output, path, elapsed=elapsed)


def _print_tests(
    result: str,
    output: Optional[str],
    source_path: Path,
    elapsed: Optional[float] = None,
) -> None:
    if output:
        out_path = Path(output)
        if out_path.is_dir():
            out_path = out_path / f"test_{source_path.stem}.py"
        out_path.write_text(result)
        print_success(f"Tests written to {out_path}")
    else:
        console.print()
        console.print(Rule(style="dim"))
        console.print(Syntax(result, "python", theme="monokai", line_numbers=True))
        console.print(Rule(style="dim"))
        if elapsed:
            console.print(f"[dim]  ⏱  {elapsed:.1f}s[/dim]")
        console.print()
