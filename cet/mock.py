MOCK_RESPONSES = {
    "explain": """
## Summary
This module implements the PR review tool for `cet`. It extracts a git diff (from staged changes, a branch comparison, or a file), builds a prompt, sends it to Claude, and formats the output for terminal or GitHub comment display.

## Component Breakdown
**`pr_tool()`** — main entry point called by the CLI. Loads config, retrieves the diff, applies focus/conventions from `.cet.toml`, then delegates to the Claude client.

**`_get_diff()`** — handles three diff sources: a saved `.diff` file, a branch comparison via `git diff <branch>...HEAD`, or staged changes via `git diff --staged`.

**`_diff_summary()`** — produces the compact `3 files · +42 −7` line shown in the panel header.

**`_build_project_context()`** — pulls project name and framework from config to give Claude codebase awareness.

## Gotchas & Hidden Complexity
- `git diff --staged` returns empty string if nothing is staged — handled with an early exit, but the message could be clearer.
- Branch diff uses `...` (three dots) not `..` (two dots) — intentional: shows only changes on the feature branch, not the full divergence.
- `team_conventions` is passed raw from TOML — no sanitization. A malicious `.cet.toml` could inject prompt content.

## Suggested Improvements
1. Add a `--unstaged` flag — currently only staged changes are reviewed, which surprises new users.
2. Sanitize `team_conventions` before prompt injection.
3. `_get_diff()` should raise a more descriptive error when not inside a git repo.
4. Add a `--max-lines` guard — very large diffs produce poor reviews; better to warn and truncate.
5. The GitHub comment output format should include a collapsible `<details>` block for long reviews.
""",
    "pr": """
## Overall Assessment
🔄 **Request Changes**
Solid structure but two issues need addressing before merge — one security concern and one silent failure mode.

## File-by-File Review

**`cet/tools/pr_review.py`**
- Clean separation of diff retrieval from prompt building — good design.
- `_get_diff()` swallows stderr from git on non-zero exit but only prints it, doesn't raise. A failed `git diff` will produce an empty string and silently generate a useless review.
- 🔴 SECURITY: `team_conventions` from `.cet.toml` is injected directly into the prompt with no sanitization. A shared repo with a malicious `.cet.toml` could manipulate Claude's output.

## Flags
🔴 SECURITY — `team_conventions` prompt injection via unsanitized TOML input
🟠 BUG — silent empty diff when `git diff` fails

## Summary
- Sanitize `team_conventions` before prompt injection
- Raise an exception (don't just print) when `git diff` returns non-zero
- Add a minimum diff length check before calling the API
""",
    "test": '''import pytest
from unittest.mock import MagicMock, patch
from cet.tools.pr_review import pr_tool, _get_diff, _diff_summary

SAMPLE_DIFF = """diff --git a/auth.py b/auth.py
--- a/auth.py
+++ b/auth.py
@@ -1,3 +1,6 @@
+def login(user_id):
+    query = f"SELECT * FROM users WHERE id = {user_id}"
+    return db.execute(query)
"""

def test_diff_summary_counts_correctly():
    summary = _diff_summary(SAMPLE_DIFF)
    assert "+3" in summary
    assert "auth.py" not in summary  # summary is compact

def test_diff_summary_empty():
    assert "+0" in _diff_summary("")

@patch("cet.tools.pr_review.subprocess.run")
def test_get_diff_staged(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout=SAMPLE_DIFF)
    result = _get_diff(branch=None, diff_file=None)
    assert "login" in result
    mock_run.assert_called_once_with(["git", "diff", "--staged"], capture_output=True, text=True)

@patch("cet.tools.pr_review.subprocess.run")
def test_get_diff_branch(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout=SAMPLE_DIFF)
    result = _get_diff(branch="main", diff_file=None)
    assert "git" in str(mock_run.call_args)
    assert "main" in str(mock_run.call_args)
''',
    "spec": """openapi: 3.1.0
info:
  title: PR Review Tool API
  version: 0.1.0
paths:
  /review:
    post:
      summary: Submit code diff for review
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                diff:
                  type: string
                focus:
                  type: string
                  enum: [security, performance, style]
      responses:
        '200':
          description: Review result
          content:
            application/json:
              schema:
                type: object
                properties:
                  verdict:
                    type: string
                  summary:
                    type: string
""",
}

def get_mock_response(tool_name: str) -> str:
    return MOCK_RESPONSES.get(tool_name, MOCK_RESPONSES["explain"])
