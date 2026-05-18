from __future__ import annotations
import pytest
from unittest.mock import patch, MagicMock
from cet.prompts.env_audit import build_user_prompt, SYSTEM


# ── Prompt builder ────────────────────────────────────────────────────────────

def test_prompt_contains_content():
    prompt = build_user_prompt(content="DATABASE_URL=postgres://localhost/db")
    assert "DATABASE_URL" in prompt

def test_prompt_with_actual_env():
    prompt = build_user_prompt(
        content="DATABASE_URL=\nREDIS_URL=",
        has_actual=True,
        actual_content="DATABASE_URL=postgres://localhost/db",
    )
    assert "postgres://localhost/db" in prompt

def test_prompt_without_actual_has_no_actual_block():
    prompt = build_user_prompt(content="DATABASE_URL=", has_actual=False)
    assert "Actual .env" not in prompt

def test_prompt_with_project_context():
    prompt = build_user_prompt(content="KEY=val", project_context="Project: billing-api")
    assert "billing-api" in prompt


# ── System prompt ─────────────────────────────────────────────────────────────

def test_system_has_summary_section():
    assert "Summary" in SYSTEM

def test_system_has_missing_variables_section():
    assert "Missing Variables" in SYSTEM

def test_system_has_security_flags():
    assert "Security Flags" in SYSTEM

def test_system_has_recommendations():
    assert "Recommendations" in SYSTEM

def test_system_has_critical_flag():
    assert "CRITICAL" in SYSTEM

def test_system_has_warning_flag():
    assert "WARNING" in SYSTEM


# ── Tool logic ────────────────────────────────────────────────────────────────

def test_env_tool_missing_file_exits(tmp_path):
    from cet.tools.env_audit import env_tool
    with pytest.raises(SystemExit):
        env_tool(file=str(tmp_path / "nonexistent.env"), actual=None, doc=False, no_cache=True, mock=False)

def test_env_tool_mock_mode(tmp_path):
    env_file = tmp_path / ".env.example"
    env_file.write_text("DATABASE_URL=\nSECRET_KEY=dev-secret-123\n")
    from cet.tools.env_audit import env_tool
    env_tool(file=str(env_file), actual=None, doc=False, no_cache=True, mock=True)

def test_env_tool_missing_actual_exits(tmp_path):
    env_file = tmp_path / ".env.example"
    env_file.write_text("DATABASE_URL=\n")
    from cet.tools.env_audit import env_tool
    with pytest.raises(SystemExit):
        env_tool(file=str(env_file), actual=str(tmp_path / "nonexistent.env"), doc=False, no_cache=True, mock=False)
