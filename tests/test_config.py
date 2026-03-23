"""Tests for config loading."""
from __future__ import annotations
import os
import pytest
from unittest.mock import patch


def test_config_raises_without_api_key():
    from cet.config import Config
    with patch.dict(os.environ, {}, clear=True):
        # Remove key if present
        os.environ.pop("ANTHROPIC_API_KEY", None)
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            Config.load()

def test_config_loads_api_key_from_env():
    from cet.config import Config
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-123"}):
        config = Config.load()
        assert config.api_key == "sk-test-123"

def test_config_default_model():
    from cet.config import Config
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-123"}):
        config = Config.load()
        assert "claude" in config.model

def test_config_default_cache_enabled():
    from cet.config import Config
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test-123"}):
        config = Config.load()
        assert config.cache_enabled is True

def test_config_loads_toml(tmp_path):
    from cet.config import Config
    toml = tmp_path / ".cet.toml"
    toml.write_text("""
[project]
name = "my-api"
framework = "fastapi"

[claude]
model = "claude-opus-4-5"
cache = false
""")
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "sk-test"}):
        with patch.object(Config, "_find_toml", return_value=toml):
            config = Config.load()
            assert config.project_name == "my-api"
            assert config.project_framework == "fastapi"
            assert config.model == "claude-opus-4-5"
            assert config.cache_enabled is False
