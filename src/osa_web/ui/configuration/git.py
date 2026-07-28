from __future__ import annotations

import streamlit as st

from osa_web.ui.configuration.schema import configuration_callback, current_section


@st.fragment
def render_git_settings_block() -> None:
    with st.container(border=True):
        st.markdown(
            '<h5 style="text-align: center;">Git Settings</h5>',
            unsafe_allow_html=True,
        )

        current_git = current_section("git")

        st.text_input(
            label="Branch",
            key="configuration-git-branch",
            on_change=configuration_callback,
            args=["git", "branch", "configuration-git-branch"],
            value=current_git["branch"],
            help="""Branch name of the GitHub repository
                `Default: Default repository branch`""",
        )
        left, right = st.columns(2)
        with left:
            st.checkbox(
                label="No pull request",
                key="configuration-git-no-pull-request",
                on_change=configuration_callback,
                args=["git", "no-pull-request", "configuration-git-no-pull-request"],
                value=current_git["no-pull-request"],
                help="""Avoid create pull request for target repository
                `Default: False`""",
            )
        with right:
            st.checkbox(
                label="No fork",
                key="configuration-git-no-fork",
                on_change=configuration_callback,
                args=["git", "no-fork", "configuration-git-no-fork"],
                value=current_git["no-fork"],
                help="""Avoid create fork for target repository
                        `Default: False`""",
            )
