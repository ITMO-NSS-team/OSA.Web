from __future__ import annotations

import copy
import os
from pathlib import Path
from typing import Any

import toml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"
DEFAULT_CONFIG_PATH = CONFIG_DIR / "default.toml"
LOCAL_CONFIG_PATH = CONFIG_DIR / "local.toml"
LEGACY_CONFIG_PATH = PROJECT_ROOT / "config.toml"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"


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
    return toml.load(path)


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load default settings plus optional local overrides.

    Precedence is: config/default.toml, legacy root config.toml, config/local.toml,
    explicit path or OSA_WEB_CONFIG.
    """
    config = _load_toml(DEFAULT_CONFIG_PATH)

    for path in (LEGACY_CONFIG_PATH, LOCAL_CONFIG_PATH):
        config = _deep_merge(config, _load_toml(path))

    explicit_path = config_path or os.getenv("OSA_WEB_CONFIG")
    if explicit_path:
        config = _deep_merge(config, _load_toml(resolve_project_path(explicit_path)))

    return config


def resolve_project_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def get_runtime_path(config: dict[str, Any], key: str) -> Path:
    return resolve_project_path(config["paths"][key])


def ensure_runtime_paths(config: dict[str, Any]) -> None:
    get_runtime_path(config, "log").parent.mkdir(parents=True, exist_ok=True)
    get_runtime_path(config, "tmp").mkdir(parents=True, exist_ok=True)


def asset_path(filename: str) -> Path:
    return ASSETS_DIR / filename
