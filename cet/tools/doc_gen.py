from __future__ import annotations
from typing import Optional
"""cet doc — add inline docs and docstrings to any code file."""

import time
from pathlib import Path
from rich.syntax import Syntax
from rich.rule import Rule

from cet.config import Config
from cet.client import ClaudeClient
from cet.core.chunker import read_file
from cet.core.ui import console, print_header, print_waiting, print_success, print_error, file_meta
from cet.prompts import doc_gen as prompts

EXTENSION_TO_LANGUAGE = {
    ".py": "python", ".php": "php", ".go": "go", ".ts": "typescript",
    ".js": "javascript", ".rb": "ruby", ".java": "java", ".rs": "rust",
}


def doc_tool(
    file: str,
    output: Optional[str],
    inplace: bool,
    no_cache: bool,
    mock: bool = False,
) -> None:
    path = Path(file)

    if not path.exists():
        print_error(f"File not found: {file}")
        raise SystemExit(1)

    language = EXTENSION_TO_LANGUAGE.get(path.suffix, "text")
    meta = file_meta(path, language)
    if inplace:
        meta["mode"] = "in-place"

    print_header("doc", file, meta)

    if mock:
        from cet.mock import get_mock_response
        result = get_mock_response("doc")
        _write_output(result, output, path, inplace, language)
        return

    config = Config.load()
    code = read_file(file)
    project_context = _build_project_context(config)

    user_prompt = prompts.build_user_prompt(
        filename=path.name,
        language=language,
        code=code,
        project_context=project_context,
    )

    client = ClaudeClient(config)
    start = time.time()
    with print_waiting("Generating documentation..."):
        result = client.ask(
            system=prompts.SYSTEM,
            user=user_prompt,
            tool_name="doc",
            use_cache=not no_cache,
            stream=False,
        )
    elapsed = time.time() - start

    _write_output(result, output, path, inplace, language, elapsed=elapsed)


def _write_output(
    result: str,
    output: Optional[str],
    source_path: Path,
    inplace: bool,
    language: str,
    elapsed: Optional[float] = None,
) -> None:
    if inplace:
        source_path.write_text(result)
        print_success(f"Documentation added in-place: {source_path}")
    elif output:
        Path(output).write_text(result)
        print_success(f"Documented file written to {output}")
    else:
        console.print()
        console.print(Rule(style="dim"))
        console.print(Syntax(result, language, theme="monokai", line_numbers=True))
        console.print(Rule(style="dim"))
        if elapsed:
            console.print(f"[dim]  ⏱  {elapsed:.1f}s[/dim]")
        console.print()


def _build_project_context(config) -> str:
    parts = []
    if config.project_name:
        parts.append(f"Project: {config.project_name}")
    if config.project_framework:
        parts.append(f"Framework: {config.project_framework}")
    return "\n".join(parts)
