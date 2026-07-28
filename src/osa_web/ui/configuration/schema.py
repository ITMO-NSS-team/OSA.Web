from __future__ import annotations

from typing import Any

import streamlit as st


def configuration_callback(table: str, key: str, value: str) -> None:
    st.session_state.configuration[st.session_state.mode_select][table][key] = st.session_state[value]


def current_section(section: str) -> dict[str, Any]:
    return st.session_state.configuration[st.session_state.mode_select][section]
