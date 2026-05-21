from __future__ import annotations
from typing import Optional
"""Prompt templates for the changelog generator."""

SYSTEM = """You are a senior backend engineer writing a CHANGELOG entry from git commits.

Output rules:
- Output ONLY the changelog entry. No preamble, no explanation.
- Follow Keep a Changelog format (https://keepachangelog.com)
- Start with the version header: ## [Unreleased] - YYYY-MM-DD
- Use exactly these sections, only if relevant:
  ### Added
  ### Changed  
  ### Deprecated
  ### Removed
  ### Fixed
  ### Security
- Each item: one line, starts with a capital letter, no full stop at end
- Group related commits into single changelog items — don't list every commit separately
- Skip noise: merge commits, version bumps, typo fixes, "wip" commits
- Infer intent from commit messages — "fix auth token expiry bug" → Fixed section
- Conventional commits map directly: feat: → Added, fix: → Fixed, chore: → skip
- If a commit message is unclear, use your best judgment based on the diff summary"""

USER_TEMPLATE = """Generate a CHANGELOG entry from these git commits.

Repository: {repo_name}
Date: {date}{context_block}

Commits:
{commits}"""

def build_user_prompt(
    commits: str,
    repo_name: str = "unknown",
    date: str = "",
    project_context: str = "",
) -> str:
    context_block = f"\nProject context: {project_context}" if project_context else ""
    return USER_TEMPLATE.format(
        commits=commits,
        repo_name=repo_name,
        date=date,
        context_block=context_block,
    )
