from __future__ import annotations

from typing import Any

import streamlit as st

from osa_web.state import keys

BASE_URL_PRESETS = {
    "OpenAI": "https://api.openai.com/v1",
    "OpenRouter": "https://openrouter.ai/api/v1",
}
CUSTOM_ENDPOINT = "Custom"


def endpoint_choice(llm: dict[str, Any]) -> str:
    if llm["api"] == "openai":
        for name, url in BASE_URL_PRESETS.items():
            if llm["base-url"].rstrip("/") == url:
                return name
    return CUSTOM_ENDPOINT


def selected_configuration_mode() -> str:
    if st.session_state.get(keys.WORK_MODE) == keys.WORK_MODE_AGENTIC:
        return "agentic"
    return st.session_state.get("mode_select", "quality")


def reset_configuration_widgets() -> None:
    # The widgets already read their defaults from the selected configuration.
    # Clearing their old keys lets them adopt those defaults without assigning a
    # Session State value as well as a widget value/index/default.
    for name in list(st.session_state):
        if name.startswith("configuration-") and name not in {
            keys.CONFIGURATION_PRESET,
            keys.CONFIGURATION_API_KEY,
            keys.CONFIGURATION_AGENTIC_API_KEY,
        }:
            del st.session_state[name]


def configuration_callback(table: str, key: str, value: str) -> None:
    # A mode change can remove widgets absent from the new mode. Fragment callbacks
    # for those widgets can still arrive during the rerun; their values are stale.
    mode_config = st.session_state[keys.CONFIGURATION][selected_configuration_mode()]
    if value in st.session_state and key in mode_config.get(table, {}):
        mode_config[table][key] = st.session_state[value]


def current_section(section: str) -> dict[str, Any]:
    return st.session_state.configuration[selected_configuration_mode()][section]
