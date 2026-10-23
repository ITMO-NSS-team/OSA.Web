from __future__ import annotations

import streamlit as st

from osa_web.state import keys
from osa_web.ui.configuration.general import render_osa_settings_block
from osa_web.ui.configuration.git import render_git_settings_block
from osa_web.ui.configuration.llm import render_llm_settings_block
from osa_web.ui.configuration.schema import reset_configuration_widgets
from osa_web.ui.configuration.workflows import render_workflows_settings_block


def _select_pipeline_preset() -> None:
    st.session_state[keys.MODE_SELECT] = st.session_state[keys.CONFIGURATION_PRESET]
    reset_configuration_widgets()


def render_configuration_tab() -> None:
    if st.session_state.get(keys.WORK_MODE) == keys.WORK_MODE_AGENTIC:
        st.caption("Agentic conversation: configure Git publishing and the language model.")
        left, right = st.columns(2)
        with left:
            render_git_settings_block()
        with right:
            render_llm_settings_block()
        return

    selected_preset = st.session_state.get(keys.MODE_SELECT, "quality")
    if st.session_state.get(keys.CONFIGURATION_PRESET) != selected_preset:
        st.session_state[keys.CONFIGURATION_PRESET] = selected_preset
    st.segmented_control(
        "Automated pipeline preset",
        ("quality", "fast"),
        key=keys.CONFIGURATION_PRESET,
        format_func=str.title,
        required=True,
        on_change=_select_pipeline_preset,
        persist_state="session",
        help="Choose which automated pipeline preset to edit and run. Default: quality.",
    )
    st.caption(f"Settings for the {selected_preset} preset.")
    left, center, right = st.columns([1, 1, 1])
    with left:
        render_git_settings_block()
        render_osa_settings_block()
    with center:
        render_workflows_settings_block()
    with right:
        render_llm_settings_block()
