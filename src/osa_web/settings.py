from __future__ import annotations

import copy
import os
import tomllib
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.toml"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
REQUIRED_CONFIG_SECTIONS = ("fast", "quality", "agentic")
RUNTIME_PATHS = {
    "log": ("OSA_WEB_LOG_PATH", "runtime/logs/osa_web.logs"),
    "tmp": ("OSA_WEB_TMP_DIR", "runtime/tmp"),
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def _load_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("rb") as file:
        return tomllib.load(file)


def validate_config(config: dict[str, Any]) -> None:
    missing_sections = [section for section in REQUIRED_CONFIG_SECTIONS if section not in config]
    if missing_sections:
        raise RuntimeError(
            "OSA.Web configuration is missing required sections: "
            f"{', '.join(missing_sections)}. Ensure config.toml is present "
            "or provide OSA_WEB_CONFIG."
        )


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load tracked settings plus an optional TOML override.

    Precedence is: config.toml, then explicit path or OSA_WEB_CONFIG.
    """
    config = _load_toml(CONFIG_PATH)

    explicit_path = config_path or os.getenv("OSA_WEB_CONFIG")
    if explicit_path:
        config = _deep_merge(config, _load_toml(resolve_project_path(explicit_path)))

    # Older web configs called the OpenRouter-compatible API "itmo" and the
    # command builder silently rewrote it to "openai". Preserve that behavior
    # only for that endpoint; a real ITMO endpoint now uses OSA's itmo provider.
    for mode in ("fast", "quality", "agentic"):
        llm = config.get(mode, {}).get("llm", {})
        host = urlsplit(llm.get("base-url", "")).hostname or ""
        if llm.get("api") == "itmo" and (
            host == "openrouter.ai" or host.endswith(".openrouter.ai")
        ):
            llm["api"] = "openai"

    validate_config(config)

    return config


def resolve_project_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def get_runtime_path(key: str) -> Path:
    env_name, default = RUNTIME_PATHS[key]
    return resolve_project_path(os.getenv(env_name) or default)


def ensure_runtime_paths() -> None:
    get_runtime_path("log").parent.mkdir(parents=True, exist_ok=True)
    get_runtime_path("tmp").mkdir(parents=True, exist_ok=True)


def asset_path(filename: str) -> Path:
    return ASSETS_DIR / filename
