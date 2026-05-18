from __future__ import annotations
import pytest
from unittest.mock import patch, MagicMock
from cet.prompts.migrate import build_analyse_prompt, build_translate_prompt, SYSTEM_ANALYSE, SYSTEM_TRANSLATE


# ── Prompt builders ───────────────────────────────────────────────────────────

def test_analyse_prompt_contains_filename():
    prompt = build_analyse_prompt(filename="auth.php", code="<?php echo 'hello';")
    assert "auth.php" in prompt

def test_analyse_prompt_contains_code():
    prompt = build_analyse_prompt(filename="auth.php", code="<?php echo 'hello';")
    assert "echo 'hello'" in prompt

def test_analyse_prompt_contains_framework():
    prompt = build_analyse_prompt(filename="auth.php", code="<?php", framework="django")
    assert "django" in prompt

def test_analyse_prompt_with_context():
    prompt = build_analyse_prompt(filename="auth.php", code="<?php", project_context="Project: billing")
    assert "billing" in prompt

def test_translate_prompt_contains_filename():
    prompt = build_translate_prompt(filename="auth.php", code="<?php echo 'hello';")
    assert "auth.php" in prompt

def test_translate_prompt_contains_code():
    prompt = build_translate_prompt(filename="auth.php", code="<?php echo 'hello';")
    assert "echo 'hello'" in prompt

def test_translate_default_framework_is_fastapi():
    prompt = build_translate_prompt(filename="auth.php", code="<?php")
    assert "fastapi" in prompt


# ── System prompts ────────────────────────────────────────────────────────────

def test_analyse_system_has_overview():
    assert "Overview" in SYSTEM_ANALYSE

def test_analyse_system_has_framework_mapping():
    assert "Framework Mapping" in SYSTEM_ANALYSE

def test_analyse_system_has_security_improvements():
    assert "Security Improvements" in SYSTEM_ANALYSE

def test_analyse_system_has_phpisms():
    assert "PHP-isms" in SYSTEM_ANALYSE

def test_translate_system_outputs_only_python():
    assert "Output ONLY" in SYSTEM_TRANSLATE

def test_translate_system_has_migration_comments():
    assert "MIGRATION:" in SYSTEM_TRANSLATE

def test_translate_system_has_security_comments():
    assert "SECURITY:" in SYSTEM_TRANSLATE


# ── Tool logic ────────────────────────────────────────────────────────────────

def test_migrate_tool_missing_file_exits(tmp_path):
    from cet.tools.migrate import migrate_tool
    with pytest.raises(SystemExit):
        migrate_tool(
            file=str(tmp_path / "nonexistent.php"),
            framework="fastapi", output=None,
            translate=False, report=False,
            no_cache=True, mock=False,
        )

def test_migrate_tool_mock_analyse(tmp_path):
    php_file = tmp_path / "auth.php"
    php_file.write_text("<?php function login() { return true; }")
    from cet.tools.migrate import migrate_tool
    migrate_tool(
        file=str(php_file),
        framework="fastapi", output=None,
        translate=False, report=False,
        no_cache=True, mock=True,
    )

def test_migrate_tool_mock_translate(tmp_path):
    php_file = tmp_path / "auth.php"
    php_file.write_text("<?php function login() { return true; }")
    from cet.tools.migrate import migrate_tool
    migrate_tool(
        file=str(php_file),
        framework="fastapi", output=None,
        translate=True, report=False,
        no_cache=True, mock=True,
    )

def test_migrate_tool_mock_writes_output(tmp_path):
    php_file = tmp_path / "auth.php"
    php_file.write_text("<?php function login() { return true; }")
    out_file = tmp_path / "auth.py"
    from cet.tools.migrate import migrate_tool
    migrate_tool(
        file=str(php_file),
        framework="fastapi", output=str(out_file),
        translate=True, report=False,
        no_cache=True, mock=True,
    )
    assert out_file.exists()
    assert len(out_file.read_text()) > 0
