from __future__ import annotations

import streamlit as st

from osa_web.ui.configuration.general import render_osa_settings_block
from osa_web.ui.configuration.git import render_git_settings_block
from osa_web.ui.configuration.llm import render_llm_settings_block
from osa_web.ui.configuration.workflows import render_workflows_settings_block


def render_configuration_tab() -> None:
    left, center, right = st.columns([1, 1, 1])
    with left:
        render_git_settings_block()
        render_osa_settings_block()
    with center:
        render_workflows_settings_block()
    with right:
        render_llm_settings_block()
