from __future__ import annotations
from typing import Optional
"""cet migrate — PHP to Python migration co-pilot."""

import time
from pathlib import Path
from rich.syntax import Syntax
from rich.rule import Rule

from cet.core.chunker import read_file, collect_files
from cet.core.ui import console, print_header, print_waiting, print_result, print_success, print_error, file_meta
from cet.prompts import migrate as prompts


def migrate_tool(
    file: str,
    framework: str,
    output: Optional[str],
    translate: bool,
    report: bool,
    no_cache: bool,
    mock: bool = False,
) -> None:
    path = Path(file)

    if not path.exists():
        print_error(f"File not found: {file}")
        raise SystemExit(1)

    mode = "translate" if translate else "report" if report else "analyse"
    meta = {"framework": framework, "mode": mode}
    if path.suffix:
        meta["lang"] = path.suffix.lstrip(".")

    print_header("migrate", file, meta)

    if mock:
        from cet.mock import get_mock_response
        result = get_mock_response("migrate")
        if translate:
            _print_code(result, output, path)
        else:
            print_result(result)
        return

    from cet.config import Config
    from cet.client import ClaudeClient

    config = Config.load()
    code = read_file(file)
    project_context = f"Project: {config.project_name}" if config.project_name else ""

    if translate:
        user_prompt = prompts.build_translate_prompt(
            filename=path.name,
            code=code,
            framework=framework,
            project_context=project_context,
        )
        system = prompts.SYSTEM_TRANSLATE
    else:
        user_prompt = prompts.build_analyse_prompt(
            filename=path.name,
            code=code,
            framework=framework,
            project_context=project_context,
        )
        system = prompts.SYSTEM_ANALYSE

    client = ClaudeClient(config)
    start = time.time()
    with print_waiting(f"{'Translating' if translate else 'Analysing'} PHP → Python..."):
        result = client.ask(
            system=system,
            user=user_prompt,
            tool_name="migrate",
            use_cache=not no_cache,
            stream=False,
        )
    elapsed = time.time() - start

    if translate:
        _print_code(result, output, path, elapsed=elapsed)
    else:
        print_result(result, elapsed=elapsed)


def _print_code(
    result: str,
    output: Optional[str],
    source_path: Path,
    elapsed: Optional[float] = None,
) -> None:
    if output:
        Path(output).write_text(result)
        print_success(f"Translated file written to {output}")
    else:
        console.print()
        console.print(Rule(style="dim"))
        console.print(Syntax(result, "python", theme="monokai", line_numbers=True))
        console.print(Rule(style="dim"))
        if elapsed:
            console.print(f"[dim]  ⏱  {elapsed:.1f}s[/dim]")
        console.print()
