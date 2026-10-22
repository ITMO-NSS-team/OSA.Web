from __future__ import annotations

from typing import Any

import streamlit as st

from osa_web.state import keys


def selected_configuration_mode() -> str:
    if st.session_state.get(keys.WORK_MODE) == keys.WORK_MODE_AGENTIC:
        return "agentic"
    return st.session_state.get("mode_select", "quality")


def reset_configuration_widgets() -> None:
    for name in list(st.session_state):
        if name.startswith("configuration-") and name not in {
            "configuration-api-key",
            "configuration-agentic-api-key",
        }:
            del st.session_state[name]


def configuration_callback(table: str, key: str, value: str) -> None:
    st.session_state.configuration[selected_configuration_mode()][table][key] = st.session_state[value]


def current_section(section: str) -> dict[str, Any]:
    return st.session_state.configuration[selected_configuration_mode()][section]
