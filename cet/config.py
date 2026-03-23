from __future__ import annotations
"""
Configuration loader — reads .cet.toml and environment variables.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Optional

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]


DEFAULT_MODEL = "claude-sonnet-4-5"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_CACHE_TTL = 3600


@dataclass
class ToolConfig:
    focus: Optional[str] = None
    framework: Optional[str] = None
    output_dir: Optional[str] = None
    style: Optional[str] = None
    team_conventions: Optional[str] = None
    servers: list[str] = field(default_factory=list)
    output: Optional[str] = None


@dataclass
class Config:
    api_key: str
    model: str = DEFAULT_MODEL
    max_tokens: int = DEFAULT_MAX_TOKENS
    cache_enabled: bool = True
    cache_ttl: int = DEFAULT_CACHE_TTL

    project_name: Optional[str] = None
    project_language: Optional[str] = None
    project_framework: Optional[str] = None
    project_description: Optional[str] = None

    tools: dict[str, ToolConfig] = field(default_factory=dict)
    plugin_paths: list[str] = field(default_factory=list)

    @classmethod
    def load(cls) -> "Config":
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is not set.\n"
                "Get your key at https://console.anthropic.com"
            )

        config = cls(api_key=api_key)
        toml_path = cls._find_toml()
        if toml_path:
            config._apply_toml(toml_path)

        return config

    @staticmethod
    def _find_toml() -> Optional[Path]:
        current = Path.cwd()
        for parent in [current, *current.parents]:
            candidate = parent / ".cet.toml"
            if candidate.exists():
                return candidate
        return None

    def _apply_toml(self, path: Path) -> None:
        with open(path, "rb") as f:
            data = tomllib.load(f)

        project = data.get("project", {})
        self.project_name = project.get("name")
        self.project_language = project.get("language")
        self.project_framework = project.get("framework")
        self.project_description = project.get("description")

        claude_cfg = data.get("claude", {})
        self.model = claude_cfg.get("model", self.model)
        self.max_tokens = claude_cfg.get("max_tokens", self.max_tokens)
        self.cache_enabled = claude_cfg.get("cache", self.cache_enabled)
        self.cache_ttl = claude_cfg.get("cache_ttl", self.cache_ttl)

        for tool_name, tool_data in data.get("tools", {}).items():
            self.tools[tool_name] = ToolConfig(**{
                k: v for k, v in tool_data.items()
                if k in ToolConfig.__dataclass_fields__
            })

        self.plugin_paths = data.get("plugins", {}).get("paths", [])
