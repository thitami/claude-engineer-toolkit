from __future__ import annotations
from typing import Optional
"""cet explain — explain any code file in plain English."""

import time
from pathlib import Path

from cet.config import Config
from cet.client import ClaudeClient
from cet.core.chunker import read_file, chunk_text
from cet.core.ui import console, print_header, print_waiting, print_result, print_success, print_error, file_meta
from cet.prompts import explain as prompts

EXTENSION_TO_LANGUAGE = {
    ".py": "python", ".php": "php", ".go": "go", ".ts": "typescript",
    ".js": "javascript", ".rb": "ruby", ".java": "java", ".rs": "rust",
    ".sql": "sql", ".sh": "bash", ".yaml": "yaml", ".yml": "yaml",
}


def explain_tool(
    file: str,
    focus: Optional[str],
    fmt: str,
    output: Optional[str],
    no_cache: bool,
    mock: bool = False,
) -> None:
    path = Path(file)

    if not path.exists():
        print_error(f"File not found: {file}")
        raise SystemExit(1)

    language = EXTENSION_TO_LANGUAGE.get(path.suffix, "text")
    meta = file_meta(path, language)
    if focus:
        meta["focus"] = focus

    print_header("explain", file, meta)

    config = Config.load()
    client = ClaudeClient(config)
    code = read_file(file)
    project_context = _build_project_context(config)

    chunks = chunk_text(code)
    if len(chunks) > 1:
        console.print(f"[dim]  Large file — processing in {len(chunks)} chunks[/dim]")

    results = []
    for i, chunk in enumerate(chunks):
        chunk_label = f"chunk {i+1}/{len(chunks)}" if len(chunks) > 1 else "analyzing"

        if mock:
            from cet.mock import get_mock_response
            result = get_mock_response("explain")
        else:
            user_prompt = prompts.build_user_prompt(
                filename=path.name,
                language=language,
                code=chunk,
                focus=focus,
                project_context=project_context,
            )
            start = time.time()
            with print_waiting(f"Asking Claude ({chunk_label})..."):
                result = client.ask(
                    system=prompts.SYSTEM,
                    user=user_prompt,
                    tool_name="explain",
                    use_cache=not no_cache,
                    stream=False,
                )
            elapsed = time.time() - start

        results.append(result)

    final = "\n\n---\n\n".join(results)

    if output:
        Path(output).write_text(final)
        print_success(f"Written to {output}")
    else:
        print_result(final, elapsed=elapsed if not mock else None)


def _build_project_context(config: Config) -> str:
    parts = []
    if config.project_name:
        parts.append(f"Project: {config.project_name}")
    if config.project_framework:
        parts.append(f"Framework: {config.project_framework}")
    if config.project_description:
        parts.append(f"Description: {config.project_description}")
    return "\n".join(parts)
