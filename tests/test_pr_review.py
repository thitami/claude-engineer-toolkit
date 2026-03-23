"""Tests for the PR review tool — prompts and tool logic."""
from __future__ import annotations
import pytest
from unittest.mock import patch, MagicMock

from cet.prompts.pr_review import build_user_prompt, SYSTEM

SAMPLE_DIFF = """\
diff --git a/src/auth.py b/src/auth.py
--- a/src/auth.py
+++ b/src/auth.py
@@ -10,4 +10,7 @@
+    query = f"SELECT * FROM users WHERE id = {user_id}"
+    result = db.execute(query)
+    return result is not None
"""

# ── Prompt builder ────────────────────────────────────────────────────────────

def test_prompt_contains_diff():
    prompt = build_user_prompt(diff=SAMPLE_DIFF)
    assert "SELECT" in prompt

def test_prompt_with_focus():
    prompt = build_user_prompt(diff=SAMPLE_DIFF, focus="security")
    assert "security" in prompt

def test_prompt_without_focus_has_no_focus_line():
    prompt = build_user_prompt(diff=SAMPLE_DIFF, focus=None)
    assert "Review focus:" not in prompt

def test_prompt_with_conventions():
    prompt = build_user_prompt(diff=SAMPLE_DIFF, team_conventions="- No raw SQL")
    assert "No raw SQL" in prompt

def test_prompt_without_conventions_has_no_conventions_block():
    prompt = build_user_prompt(diff=SAMPLE_DIFF, team_conventions="")
    assert "Team conventions" not in prompt

def test_prompt_with_project_context():
    prompt = build_user_prompt(diff=SAMPLE_DIFF, project_context="Project: api")
    assert "api" in prompt


# ── System prompt ─────────────────────────────────────────────────────────────

def test_system_has_verdict_section():
    assert "Verdict" in SYSTEM

def test_system_has_approve_option():
    assert "Approve" in SYSTEM

def test_system_has_request_changes():
    assert "Request Changes" in SYSTEM

def test_system_has_security_flag():
    assert "SECURITY" in SYSTEM

def test_system_has_bug_flag():
    assert "BUG" in SYSTEM

def test_system_demands_lead_with_verdict():
    assert "verdict" in SYSTEM.lower()


# ── _diff_summary ─────────────────────────────────────────────────────────────

def test_diff_summary_counts_additions():
    from cet.tools.pr_review import _diff_summary
    result = _diff_summary(SAMPLE_DIFF)
    assert "+3" in result

def test_diff_summary_counts_files():
    from cet.tools.pr_review import _diff_summary
    result = _diff_summary(SAMPLE_DIFF)
    assert "1 files" in result or "1" in result

def test_diff_summary_empty_diff():
    from cet.tools.pr_review import _diff_summary
    result = _diff_summary("")
    assert "+0" in result


# ── _get_diff ─────────────────────────────────────────────────────────────────

def test_get_diff_reads_file(tmp_path):
    from cet.tools.pr_review import _get_diff
    diff_file = tmp_path / "my.diff"
    diff_file.write_text(SAMPLE_DIFF)
    result = _get_diff(branch=None, diff_file=str(diff_file))
    assert "SELECT" in result

@patch("cet.tools.pr_review.subprocess.run")
def test_get_diff_staged(mock_run):
    from cet.tools.pr_review import _get_diff
    mock_run.return_value = MagicMock(returncode=0, stdout=SAMPLE_DIFF)
    result = _get_diff(branch=None, diff_file=None)
    assert result == SAMPLE_DIFF
    mock_run.assert_called_once_with(["git", "diff", "--staged"], capture_output=True, text=True)

@patch("cet.tools.pr_review.subprocess.run")
def test_get_diff_branch(mock_run):
    from cet.tools.pr_review import _get_diff
    mock_run.return_value = MagicMock(returncode=0, stdout=SAMPLE_DIFF)
    _get_diff(branch="main", diff_file=None)
    args = mock_run.call_args[0][0]
    assert "main...HEAD" in args

@patch("cet.tools.pr_review.subprocess.run")
def test_get_diff_git_failure_exits(mock_run):
    from cet.tools.pr_review import _get_diff
    mock_run.return_value = MagicMock(returncode=1, stderr="not a git repo")
    with pytest.raises(SystemExit):
        _get_diff(branch=None, diff_file=None)


# ── Tool logic ────────────────────────────────────────────────────────────────

def test_pr_tool_mock_mode():
    from cet.tools.pr_review import pr_tool
    # Should complete without hitting git or API
    pr_tool(branch=None, diff_file=None, focus=None, output="terminal", no_cache=True, mock=True)
