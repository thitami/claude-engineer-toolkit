from __future__ import annotations
from typing import Optional
"""cet changelog — generate CHANGELOG entries from git commits."""

import time
import subprocess
from datetime import date
from pathlib import Path
from rich.syntax import Syntax
from rich.rule import Rule

from cet.core.ui import console, print_header, print_waiting, print_result, print_success, print_error
from cet.prompts import changelog as prompts


def changelog_tool(
    since: Optional[str],
    commits: int,
    output: Optional[str],
    no_cache: bool,
    mock: bool = False,
) -> None:
    # Get repo name
    repo_name = _get_repo_name()

    # Get commits
    commit_log = _get_commits(since=since, count=commits)
    if not commit_log.strip():
        print_error("No commits found.")
        raise SystemExit(0)

    commit_count = len([l for l in commit_log.splitlines() if l.startswith("commit")])
    meta = {"commits": str(commit_count)}
    if since:
        meta["since"] = since

    print_header("changelog", repo_name, meta)

    if mock:
        from cet.mock import get_mock_response
        result = get_mock_response("changelog")
        _write_output(result, output)
        return

    from cet.config import Config
    from cet.client import ClaudeClient

    config = Config.load()
    project_context = f"Project: {config.project_name}" if config.project_name else ""
    today = date.today().isoformat()

    user_prompt = prompts.build_user_prompt(
        commits=commit_log,
        repo_name=repo_name,
        date=today,
        project_context=project_context,
    )

    client = ClaudeClient(config)
    start = time.time()
    with print_waiting("Generating changelog entry..."):
        result = client.ask(
            system=prompts.SYSTEM,
            user=user_prompt,
            tool_name="changelog",
            use_cache=not no_cache,
            stream=False,
        )
    elapsed = time.time() - start
    _write_output(result, output, elapsed=elapsed)


def _get_commits(since: Optional[str], count: int) -> str:
    if since:
        cmd = ["git", "log", f"{since}..HEAD", "--format=commit %H%n%s%n%b%n---"]
    else:
        cmd = ["git", "log", f"-{count}", "--format=commit %H%n%s%n%b%n---"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print_error(f"git error: {result.stderr}")
        raise SystemExit(1)
    return result.stdout


def _get_repo_name() -> str:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        url = result.stdout.strip()
        return url.rstrip("/").split("/")[-1].replace(".git", "")
    return "unknown"


def _write_output(
    result: str,
    output: Optional[str],
    elapsed: Optional[float] = None,
) -> None:
    if output:
        out_path = Path(output)
        if out_path.exists():
            # Prepend to existing changelog
            existing = out_path.read_text()
            # Insert after the first line (# Changelog header)
            lines = existing.splitlines()
            if lines and lines[0].startswith("# "):
                new_content = lines[0] + "\n\n" + result + "\n\n" + "\n".join(lines[1:]).lstrip()
            else:
                new_content = result + "\n\n" + existing
            out_path.write_text(new_content)
        else:
            out_path.write_text(f"# Changelog\n\n{result}\n")
        print_success(f"Changelog written to {output}")
    else:
        console.print()
        console.print(Rule(style="dim"))
        console.print(Syntax(result, "markdown", theme="monokai"))
        console.print(Rule(style="dim"))
        if elapsed:
            console.print(f"[dim]  ⏱  {elapsed:.1f}s[/dim]")
        console.print()
