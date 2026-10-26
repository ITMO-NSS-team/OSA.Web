"""Read-only view of public, curated OSA runs."""

from __future__ import annotations

import streamlit as st

from osa_web.past_runs import PastRun, load_past_runs


def _render_run(index: int, run: PastRun) -> None:
    with st.expander(f"{index}. {run.repository_name}"):
        st.markdown(f"[View repository]({run.repository_url})")
        st.caption(f"{run.completed_at} · {run.outcome.capitalize()}")
        if run.preset:
            st.write(f"Preset: {run.preset}")
        if run.request:
            st.write(f"Request: {run.request}")
        st.write(run.summary)
        st.markdown("**Key steps**")
        for step in run.steps:
            st.markdown(f"- {step}")
        if run.pull_request_url:
            st.link_button("View pull request", run.pull_request_url)


def render_past_runs_tab(work_mode: str) -> None:
    st.subheader("Past runs")
    st.caption("Curated results from earlier OSA runs. These examples are available to everyone.")
    try:
        runs = load_past_runs()
    except (OSError, TypeError, ValueError) as exc:
        st.error(f"Could not load past runs: {exc}")
        return
    selected = [run for run in runs if run.work_mode == work_mode]
    if not selected:
        st.info("No past runs have been added for this work mode yet.")
        return
    for index, run in enumerate(selected, start=1):
        _render_run(index, run)
