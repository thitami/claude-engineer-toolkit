from __future__ import annotations
from typing import Optional
"""Prompt templates for the env audit tool."""

SYSTEM = """You are a senior backend engineer auditing environment variable configuration.
You are direct, specific, and security-conscious.

Output rules:
- Structure your response with exactly these sections
- Reference actual variable names, never generic ones
- Only flag real issues — don't invent problems

## Summary
One line: overall health of this env configuration.

## Missing Variables
Variables present in .env.example but missing from .env.
Format: VAR_NAME — why it matters

## Security Flags
🔴 CRITICAL — exposed secrets, weak values, vars that must never be committed
🟠 WARNING — potentially insecure patterns, weak defaults
List each with the variable name and exact reason.
If none: write "None found."

## Undocumented Variables
Variables with no comment explaining their purpose.
For each, suggest a one-line comment.
If all documented: write "All variables documented."

## Recommendations
3-5 specific, actionable improvements. Reference actual variable names."""

USER_TEMPLATE = """Audit this environment configuration.

{example_block}{actual_block}{context_block}

{content}"""

def build_user_prompt(
    content: str,
    has_actual: bool = False,
    actual_content: str = "",
    mode: str = "audit",
    project_context: str = "",
) -> str:
    example_block = "File: .env.example\n" if not has_actual else "File: .env.example\n"
    actual_block = f"\nActual .env:\n{actual_content}\n" if has_actual else ""
    context_block = f"\nProject context: {project_context}" if project_context else ""
    return USER_TEMPLATE.format(
        content=content,
        example_block=example_block,
        actual_block=actual_block,
        context_block=context_block,
    )
