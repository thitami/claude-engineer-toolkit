from __future__ import annotations
import pytest
from unittest.mock import patch, MagicMock
from cet.prompts.changelog import build_user_prompt, SYSTEM


# ── Prompt builder ────────────────────────────────────────────────────────────

def test_prompt_contains_commits():
    prompt = build_user_prompt(commits="commit abc\nfeat: add login\n---")
    assert "feat: add login" in prompt

def test_prompt_contains_repo_name():
    prompt = build_user_prompt(commits="commit abc\n---", repo_name="my-api")
    assert "my-api" in prompt

def test_prompt_contains_date():
    prompt = build_user_prompt(commits="commit abc\n---", date="2025-05-18")
    assert "2025-05-18" in prompt

def test_prompt_with_project_context():
    prompt = build_user_prompt(commits="commit abc\n---", project_context="Project: billing")
    assert "billing" in prompt

def test_prompt_without_context_has_no_context_line():
    prompt = build_user_prompt(commits="commit abc\n---", project_context="")
    assert "Project context:" not in prompt


# ── System prompt ─────────────────────────────────────────────────────────────

def test_system_has_added_section():
    assert "Added" in SYSTEM

def test_system_has_fixed_section():
    assert "Fixed" in SYSTEM

def test_system_has_security_section():
    assert "Security" in SYSTEM

def test_system_skips_noise():
    assert "noise" in SYSTEM.lower() or "merge" in SYSTEM.lower()

def test_system_follows_keep_a_changelog():
    assert "keepachangelog" in SYSTEM.lower()


# ── Tool logic ────────────────────────────────────────────────────────────────

@patch("cet.tools.changelog.subprocess.run")
def test_changelog_tool_mock_mode(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="commit abc\nfeat: add login\n---\n")
    from cet.tools.changelog import changelog_tool
    changelog_tool(since=None, commits=10, output=None, no_cache=True, mock=True)

@patch("cet.tools.changelog.subprocess.run")
def test_changelog_tool_empty_commits_exits(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="")
    from cet.tools.changelog import changelog_tool
    with pytest.raises(SystemExit):
        changelog_tool(since=None, commits=10, output=None, no_cache=True, mock=True)

@patch("cet.tools.changelog.subprocess.run")
def test_changelog_tool_writes_to_file(mock_run, tmp_path):
    mock_run.return_value = MagicMock(returncode=0, stdout="commit abc\nfeat: add login\n---\n")
    out_file = tmp_path / "CHANGELOG.md"
    from cet.tools.changelog import changelog_tool
    changelog_tool(since=None, commits=10, output=str(out_file), no_cache=True, mock=True)
    assert out_file.exists()
    assert "Changelog" in out_file.read_text()

@patch("cet.tools.changelog.subprocess.run")
def test_changelog_tool_prepends_to_existing_file(mock_run, tmp_path):
    mock_run.return_value = MagicMock(returncode=0, stdout="commit abc\nfeat: add login\n---\n")
    out_file = tmp_path / "CHANGELOG.md"
    out_file.write_text("# Changelog\n\n## [1.0.0] - 2025-01-01\n\n### Added\n- Initial release\n")
    from cet.tools.changelog import changelog_tool
    changelog_tool(since=None, commits=10, output=str(out_file), no_cache=True, mock=True)
    content = out_file.read_text()
    assert "Initial release" in content
    assert "Unreleased" in content
