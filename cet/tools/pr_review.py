from __future__ import annotations
from typing import Optional
"""cet pr — review staged git changes or a diff like a senior engineer."""

import time
import subprocess
from pathlib import Path

from cet.config import Config
from cet.client import ClaudeClient
from cet.core.ui import console, print_header, print_waiting, print_result, print_success, print_error
from cet.prompts import pr_review as prompts

def pr_tool(
    branch: Optional[str],
    diff_file: Optional[str],
    focus: Optional[str],
    output: str,
    no_cache: bool,
    mock: bool = False,
) -> None:
    if mock:
        from cet.mock import get_mock_response
        from rich.markdown import Markdown
        print_header("pr", "mock diff", {"focus": focus} if focus else {})
        print_result(get_mock_response("pr"))
        return

    config = Config.load()
    client = ClaudeClient(config)

    diff = _get_diff(branch=branch, diff_file=diff_file)

    if not diff.strip():
        print_error("No changes found to review. Stage some changes or pass --branch.")
        raise SystemExit(0)

    pr_config = config.tools.get("pr")
    effective_focus = focus or (pr_config.focus if pr_config else None)
    team_conventions = (pr_config.team_conventions if pr_config else None) or ""

    summary = _diff_summary(diff)
    meta = {"files": summary}
    if effective_focus:
        meta["focus"] = effective_focus

    print_header("pr", branch or "staged changes", meta)

    project_context = _build_project_context(config)
    user_prompt = prompts.build_user_prompt(
        diff=diff,
        focus=effective_focus,
        project_context=project_context,
        team_conventions=team_conventions,
    )

    start = time.time()
    with print_waiting("Reviewing diff..."):
        result = client.ask(
            system=prompts.SYSTEM,
            user=user_prompt,
            tool_name="pr",
            use_cache=not no_cache,
            stream=False,
        )
    elapsed = time.time() - start

    if output == "github-comment":
        print(f"<!-- cet pr review -->\n{result}")
    else:
        print_result(result, elapsed=elapsed)


def _get_diff(branch: Optional[str], diff_file: Optional[str]) -> str:
    if diff_file:
        return Path(diff_file).read_text()
    if branch:
        result = subprocess.run(
            ["git", "diff", f"{branch}...HEAD"],
            capture_output=True, text=True
        )
    else:
        result = subprocess.run(
            ["git", "diff", "--staged"],
            capture_output=True, text=True
        )
    if result.returncode != 0:
        print_error(f"git error: {result.stderr}")
        raise SystemExit(1)
    return result.stdout


def _diff_summary(diff: str) -> str:
    files = [l[4:] for l in diff.splitlines() if l.startswith("+++ b/")]
    additions = sum(1 for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++"))
    deletions = sum(1 for l in diff.splitlines() if l.startswith("-") and not l.startswith("---"))
    return f"{len(files)} files  +{additions} −{deletions}"


def _build_project_context(config: Config) -> str:
    parts = []
    if config.project_name:
        parts.append(f"Project: {config.project_name}")
    if config.project_framework:
        parts.append(f"Framework: {config.project_framework}")
    return "\n".join(parts)
