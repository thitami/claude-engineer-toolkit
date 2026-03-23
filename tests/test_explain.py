"""Tests for the explain tool — prompts, chunker, and tool logic."""
from __future__ import annotations
import pytest
from unittest.mock import MagicMock, patch, mock_open
from pathlib import Path

from cet.prompts.explain import build_user_prompt, SYSTEM


# ── Prompt builder ────────────────────────────────────────────────────────────

def test_build_user_prompt_contains_filename():
    prompt = build_user_prompt(filename="auth.py", language="python", code="def login(): pass")
    assert "auth.py" in prompt

def test_build_user_prompt_contains_language():
    prompt = build_user_prompt(filename="auth.py", language="python", code="pass")
    assert "python" in prompt

def test_build_user_prompt_contains_code():
    prompt = build_user_prompt(filename="auth.py", language="python", code="def login(): pass")
    assert "def login(): pass" in prompt

def test_build_user_prompt_with_focus():
    prompt = build_user_prompt(filename="f.py", language="python", code="pass", focus="security")
    assert "security" in prompt

def test_build_user_prompt_without_focus_has_no_focus_line():
    prompt = build_user_prompt(filename="f.py", language="python", code="pass", focus=None)
    assert "Focus specifically on" not in prompt

def test_build_user_prompt_with_project_context():
    prompt = build_user_prompt(
        filename="f.py", language="python", code="pass",
        project_context="Project: billing-api\nFramework: fastapi",
    )
    assert "billing-api" in prompt
    assert "fastapi" in prompt

def test_build_user_prompt_without_context_has_no_context_line():
    prompt = build_user_prompt(filename="f.py", language="python", code="pass", project_context="")
    assert "Project context:" not in prompt


# ── System prompt ─────────────────────────────────────────────────────────────

def test_system_prompt_has_summary_section():
    assert "Summary" in SYSTEM

def test_system_prompt_has_component_breakdown():
    assert "Component Breakdown" in SYSTEM

def test_system_prompt_has_gotchas():
    assert "Gotchas" in SYSTEM

def test_system_prompt_has_improvements():
    assert "Improvements" in SYSTEM

def test_system_prompt_demands_symbol_names():
    assert "symbol" in SYSTEM.lower() or "function" in SYSTEM.lower()


# ── Tool logic ────────────────────────────────────────────────────────────────

def test_explain_tool_missing_file_exits(tmp_path):
    from cet.tools.explain import explain_tool
    with pytest.raises(SystemExit):
        explain_tool(
            file=str(tmp_path / "nonexistent.py"),
            focus=None, fmt="terminal", output=None,
            no_cache=True, mock=False,
        )

def test_explain_tool_mock_mode(tmp_path):
    """Mock mode should return output without hitting the API."""
    target = tmp_path / "sample.py"
    target.write_text("def hello(): return 'world'")

    from cet.tools.explain import explain_tool
    # Should not raise — mock mode bypasses API and config
    explain_tool(
        file=str(target),
        focus=None, fmt="terminal", output=None,
        no_cache=True, mock=True,
    )

def test_explain_tool_mock_writes_to_output_file(tmp_path):
    """--output flag should write result to file."""
    target = tmp_path / "sample.py"
    target.write_text("def hello(): return 'world'")
    out = tmp_path / "out.md"

    from cet.tools.explain import explain_tool
    explain_tool(
        file=str(target),
        focus=None, fmt="terminal", output=str(out),
        no_cache=True, mock=True,
    )
    assert out.exists()
    assert len(out.read_text()) > 0
