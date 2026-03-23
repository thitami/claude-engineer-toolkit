from __future__ import annotations
from typing import Optional
"""cet spec — generate OpenAPI 3.1 specs from route/controller code."""

import time
from pathlib import Path
from rich.syntax import Syntax
from rich.rule import Rule

from cet.config import Config
from cet.client import ClaudeClient
from cet.core.chunker import collect_files, read_file
from cet.core.ui import console, print_header, print_waiting, print_success, print_error
from cet.prompts import spec_gen as prompts


def spec_tool(
    path: str,
    framework: Optional[str],
    output: Optional[str],
    fmt: str,
    no_cache: bool,
    mock: bool = False,
) -> None:
    files = collect_files(path, extensions=[".py"])
    if not files:
        print_error(f"No Python files found at: {path}")
        raise SystemExit(1)

    config = Config.load()
    spec_config = config.tools.get("spec")
    effective_framework = framework or config.project_framework or "unknown"
    effective_output = output or (spec_config.output if spec_config else None)

    print_header("spec", path, {
        "framework": effective_framework,
        "files": str(len(files)),
        "format": fmt,
    })

    if mock:
        from cet.mock import get_mock_response
        result = get_mock_response("spec")
        _print_spec(result, fmt, effective_output)
        return

    code_parts = []
    for f in files:
        content = read_file(str(f))
        code_parts.append(f"# === {f} ===\n{content}")
    combined_code = "\n\n".join(code_parts)

    project_context = f"Project: {config.project_name}" if config.project_name else ""
    user_prompt = prompts.build_user_prompt(
        code=combined_code,
        framework=effective_framework,
        fmt=fmt,
        project_context=project_context,
    )

    client = ClaudeClient(config)
    start = time.time()
    with print_waiting("Generating OpenAPI spec..."):
        result = client.ask(
            system=prompts.SYSTEM,
            user=user_prompt,
            tool_name="spec",
            use_cache=not no_cache,
            stream=False,
        )
    elapsed = time.time() - start

    _print_spec(result, fmt, effective_output, elapsed=elapsed)


def _print_spec(result: str, fmt: str, output: Optional[str], elapsed: Optional[float] = None) -> None:
    if output:
        Path(output).write_text(result)
        print_success(f"OpenAPI spec written to {output}")
    else:
        console.print()
        console.print(Rule(style="dim"))
        lang = "yaml" if fmt == "yaml" else "json"
        console.print(Syntax(result, lang, theme="monokai", line_numbers=True))
        console.print(Rule(style="dim"))
        if elapsed:
            console.print(f"[dim]  ⏱  {elapsed:.1f}s[/dim]")
        console.print()
