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
REQUIRED_CONFIG_SECTIONS = ("versions", "paths", "fast", "quality")
REQUIRED_PATH_KEYS = ("log", "tmp")


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


def validate_config(config: dict[str, Any]) -> None:
    missing_sections = [
        section for section in REQUIRED_CONFIG_SECTIONS if section not in config
    ]
    if missing_sections:
        raise RuntimeError(
            "OSA.Web configuration is missing required sections: "
            f"{', '.join(missing_sections)}. Ensure config/default.toml is present "
            "or provide OSA_WEB_CONFIG."
        )

    missing_paths = [
        path_key for path_key in REQUIRED_PATH_KEYS if path_key not in config["paths"]
    ]
    if missing_paths:
        raise RuntimeError(
            "OSA.Web configuration is missing required path keys: "
            f"{', '.join(missing_paths)}."
        )


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

    validate_config(config)

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
