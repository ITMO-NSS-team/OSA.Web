"""Confirmation content shared by the automated and agentic workflows."""

import streamlit as st


def render_publishing_confirmation(repository: str) -> tuple[bool, bool]:
    st.warning(f"This run may create a fork or pull request for {repository}.")
    st.markdown("To avoid publishing, select **No fork** and **No pull request** in Configuration.")

    left, right = st.columns(2)
    with left:
        cancelled = st.button("Cancel", width="stretch", type="primary")
    with right:
        confirmed = st.button("Yes", width="stretch")
    return cancelled, confirmed
