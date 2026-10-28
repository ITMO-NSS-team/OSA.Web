"""Five-second, read-only replay of curated OSA runs."""

from __future__ import annotations

import math
import time

import streamlit as st

from osa_web.past_runs import PastRun, load_past_runs
from osa_web.state import keys
from osa_web.ui.console_output import render_console_output

REPLAY_SECONDS = 5.0
REPLAY_STATE = "past-run-replay"


def replay_frame(
    started_at: float, now: float, step_count: int, line_count: int
) -> tuple[float, int, int]:
    """Return replay fraction and the number of visible steps and log lines."""
    fraction = min(1.0, max(0.0, (now - started_at) / REPLAY_SECONDS))
    return fraction, math.ceil(step_count * fraction), math.ceil(line_count * fraction)


def _render_final_result(run: PastRun) -> None:
    if run.outcome == "completed":
        st.success(run.summary, icon=":material/check_circle:")
    elif run.outcome == "failed":
        st.error(run.summary, icon=":material/error:")
    else:
        st.warning(run.summary, icon=":material/stop_circle:")
    if run.pull_request_url:
        st.link_button("View pull request", run.pull_request_url)


def _render_console(run: PastRun, visible_lines: int) -> None:
    render_console_output(
        "\n".join(run.replay_lines[:visible_lines][-60:]),
        run.repository_url,
        expanded=True,
        downloadable=False,
    )


@st.fragment(run_every="0.5s")
def _render_replay(run: PastRun) -> None:
    state = st.session_state.get(REPLAY_STATE)
    if not state or state["id"] != run.id:
        return

    fraction, visible_steps, visible_lines = replay_frame(
        state["started_at"], time.monotonic(), len(run.steps), len(run.replay_lines)
    )
    finished = fraction >= 1.0
    status_state = (
        "running" if not finished else "complete" if run.outcome == "completed" else "error"
    )
    st.progress(fraction, text="Replay complete" if finished else "Replaying recorded run...")

    if run.work_mode == keys.WORK_MODE_AGENTIC:
        chat_column, steps_column = st.columns([0.8, 0.2], gap="medium")
        with chat_column:
            if run.request_reconstructed:
                st.caption("Opening request reconstructed from the recorded result.")
            with st.chat_message("user"):
                st.markdown(run.request or "")
            if finished:
                with st.chat_message("assistant"):
                    _render_final_result(run)
        with (
            steps_column,
            st.status(
                "Agentic steps",
                state=status_state,
                expanded=True,
                type="compact",
            ),
        ):
            for step in run.steps[:visible_steps]:
                st.caption(step)
    else:
        with st.status(
            "Pipeline steps",
            state=status_state,
            expanded=True,
        ):
            for step in run.steps[:visible_steps]:
                st.caption(step)
        if finished:
            _render_final_result(run)

    _render_console(run, visible_lines)


def render_past_runs_tab(work_mode: str) -> None:
    st.subheader("Past runs")
    st.caption(
        "Replay recorded examples in five seconds. This demo does not run OSA or publish changes."
    )
    try:
        runs = load_past_runs()
    except (OSError, TypeError, UnicodeError, ValueError) as exc:
        st.error(f"Could not load past runs: {exc}")
        return

    selected = [run for run in runs if run.work_mode == work_mode and run.replay_lines]
    if not selected:
        st.info("No replay-ready runs have been added for this work mode yet.")
        return

    by_id = {run.id: run for run in selected}
    labels = {
        run.id: f"{index}. {run.repository_name}" for index, run in enumerate(selected, start=1)
    }
    selection_key = (
        "past-runs-pipeline-selection"
        if work_mode == keys.WORK_MODE_PIPELINE
        else "past-runs-agentic-selection"
    )
    run_id = st.selectbox(
        "Repository",
        options=list(by_id),
        format_func=labels.__getitem__,
        key=selection_key,
    )
    run = by_id[run_id]
    with st.container(border=True):
        st.text_input(
            "Repository URL",
            value=run.repository_url,
            disabled=True,
            key=f"past-run-repository-{run.id}",
        )
        if run.work_mode == keys.WORK_MODE_PIPELINE:
            st.text_input(
                "Preset", value=run.preset or "", disabled=True, key=f"past-run-preset-{run.id}"
            )
        else:
            st.text_area(
                "Reconstructed request" if run.request_reconstructed else "Request",
                value=run.request or "",
                disabled=True,
                key=f"past-run-request-{run.id}",
            )
        st.caption(f"Recorded {run.completed_at} · {run.outcome.capitalize()}")
        st.link_button("View repository", run.repository_url)

    if st.button("Run demo", key="past-run-start", icon=":material/play_arrow:", type="primary"):
        st.session_state[REPLAY_STATE] = {"id": run.id, "started_at": time.monotonic()}
    _render_replay(run)
