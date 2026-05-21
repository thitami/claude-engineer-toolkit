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
        "changelog": """
## [Unreleased] - 2025-05-18

### Added
- `cet migrate` — PHP to Python migration co-pilot with analyse and translate modes
- `cet env` — audit `.env` files for missing variables, security issues, and documentation gaps
- `cet doc` — add inline docstrings and comments to any code file
- `cet test` — generate pytest scaffolds with edge cases and mocks
- Docker support with bind mount for local file access

### Changed
- PR review prompt restructured to lead with verdict before explanation, improving output quality
- Terminal UI unified across all tools with consistent header panels and rule dividers
- Response caching now keyed on file content hash for more reliable cache hits

### Fixed
- `cet pr` mock mode no longer attempts git operations before checking mock flag
- Config loading moved after mock check in all tools to avoid requiring API key in mock mode

### Security
- Added warning for `team_conventions` prompt injection via unsanitized TOML input
""",
    "migrate": """
## Overview
This is a PHP authentication module using deprecated mysql_* functions, MD5 password hashing, global state, and raw SQL queries. Migration complexity: **High**. The code has three critical security vulnerabilities that must be fixed during migration.

## Framework Mapping
- Raw PHP → FastAPI
- mysql_connect / mysql_query → SQLAlchemy
- $_COOKIE / $_SERVER → FastAPI Request object + JWT
- MD5 password hashing → bcrypt (passlib)
- Global $__sess array → Redis session store or JWT
- file_put_contents log → Python logging module

## Function-by-Function Plan

**_chk_tok($tok, $uid)**
Validates a session token. Python equivalent: a JWT verification function using python-jose. Gotcha: the current implementation stores sessions in a global array — replace with Redis or a DB-backed session store.

**login($user, $pass)**
Authenticates a user. Python equivalent: FastAPI POST /auth/login endpoint with SQLAlchemy query. Critical: replace MD5 with bcrypt. Replace raw SQL with parameterised SQLAlchemy query to fix SQL injection.

**require_role($role)**
Role-based access control. Python equivalent: FastAPI dependency with Depends(). Much cleaner in FastAPI than the current header/cookie juggling.

## PHP-isms to Watch
- `global $__sess` — global mutable state, replace with Redis or DB sessions
- `mysql_connect` — deprecated since PHP 5.5, removed in PHP 7
- `@file_put_contents` — error suppression hiding failures, replace with proper logging
- `$_COOKIE['remember']` — cookie handling needs HTTPS-only and SameSite flags in Python equivalent

## Security Improvements
1. SQL injection in login(): `$q = "SELECT * FROM users WHERE username='" . $user . "'"` — replace with parameterised query
2. MD5 password hashing — replace with bcrypt via passlib
3. Hardcoded SECRET constant — move to environment variable
4. Token uses MD5(uid + secret + seed) — replace with JWT signed with RS256

## Migration Complexity
Score: **High**
Estimated effort: 3-4 days for a solo engineer
Main blockers: session management redesign, password hash migration strategy, SQL injection cleanup
""",
    "env": """
## Summary
Configuration has 3 missing variables, 2 security flags, and 4 undocumented vars.

## Missing Variables
DATABASE_URL — required for all database connections
REDIS_URL — required for cache and session storage
SENTRY_DSN — required for error tracking in production

## Security Flags
🔴 CRITICAL: SECRET_KEY value "dev-secret-123" looks like a weak development default — must be replaced with a cryptographically random value in production
🟠 WARNING: AWS_SECRET_ACCESS_KEY is present in .env.example — secret keys should never appear in example files, use a placeholder like "your-aws-secret-key-here"

## Undocumented Variables
QUEUE_TIMEOUT — suggest: # Maximum seconds to wait for a queue job before timing out
MAX_UPLOAD_SIZE — suggest: # Maximum file upload size in bytes
DEBUG_MODE — suggest: # Set to true to enable debug logging and error pages
CACHE_TTL — suggest: # Cache time-to-live in seconds

## Recommendations
1. Replace SECRET_KEY placeholder with instructions for generating a secure value: python -c "import secrets; print(secrets.token_hex(32))"
2. Remove AWS_SECRET_ACCESS_KEY from .env.example entirely — document it as a required external secret instead
3. Add DATABASE_URL, REDIS_URL, and SENTRY_DSN to .env.example with clear placeholder values
4. Add a comment block at the top of .env.example explaining which vars are required vs optional
5. Consider splitting into .env.example (safe defaults) and .env.secrets.example (sensitive vars) to make the security boundary explicit
""",
    "doc": '''"""
Payment processor module for handling Stripe and PayPal transactions.

This module is the primary entry point for all billing operations.
It wraps third-party payment APIs and provides a unified interface
for the rest of the application.
"""
from typing import Optional

# SECURITY: API key loaded from env — never hardcode
API_KEY = os.environ.get("PAYMENT_API_KEY")


def process_payment(amount: float, currency: str, customer_id: str) -> dict:
    """Process a payment transaction.

    Args:
        amount: Transaction amount in the specified currency.
        currency: ISO 4217 currency code (e.g. "USD", "EUR").
        customer_id: Internal customer identifier.

    Returns:
        dict with keys: transaction_id, status, amount, currency.

    Raises:
        PaymentError: If the payment gateway rejects the transaction.
        ValueError: If amount is negative or currency is invalid.
    """
    # NOTE: amount validation happens here — gateway will also validate
    # but we want to fail fast before making the network call
    if amount <= 0:
        raise ValueError(f"Amount must be positive, got {amount}")

    return _call_gateway(amount, currency, customer_id)


def _call_gateway(amount: float, currency: str, customer_id: str) -> dict:
    """Internal gateway call — do not use directly.

    Retries up to 3 times on network errors (not on payment failures).
    """
    # SECURITY: customer_id is passed as a parameter, not interpolated
    # into a query string — safe against injection
    pass
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
