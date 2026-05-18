from __future__ import annotations
from typing import Optional
"""cet env — audit .env files for missing vars, security issues, and documentation."""

import time
from pathlib import Path
from rich.rule import Rule

from cet.core.ui import console, print_header, print_waiting, print_result, print_success, print_error, file_meta
from cet.prompts import env_audit as prompts


def env_tool(
    file: str,
    actual: Optional[str],
    doc: bool,
    no_cache: bool,
    mock: bool = False,
) -> None:
    path = Path(file)

    if not path.exists():
        print_error(f"File not found: {file}")
        raise SystemExit(1)

    meta = {"mode": "diff" if actual else "doc" if doc else "audit"}
    if actual:
        meta["diff"] = actual

    print_header("env", file, meta)

    # Validate actual file exists before loading config
    actual_path = None
    if actual:
        actual_path = Path(actual)
        if not actual_path.exists():
            print_error(f"Actual .env file not found: {actual}")
            raise SystemExit(1)

    if mock:
        from cet.mock import get_mock_response
        print_result(get_mock_response("env"))
        return

    from cet.config import Config
    from cet.client import ClaudeClient

    config = Config.load()
    content = path.read_text()
    actual_content = ""
    has_actual = False

    if actual_path:
        actual_content = actual_path.read_text()
        has_actual = True

    project_context = f"Project: {config.project_name}" if config.project_name else ""
    user_prompt = prompts.build_user_prompt(
        content=content,
        has_actual=has_actual,
        actual_content=actual_content,
        mode="doc" if doc else "audit",
        project_context=project_context,
    )

    client = ClaudeClient(config)
    start = time.time()
    with print_waiting("Auditing environment configuration..."):
        result = client.ask(
            system=prompts.SYSTEM,
            user=user_prompt,
            tool_name="env",
            use_cache=not no_cache,
            stream=False,
        )
    elapsed = time.time() - start
    print_result(result, elapsed=elapsed)
