from __future__ import annotations

import copy
import os
import tempfile
from typing import Any

import streamlit as st

from osa_web.settings import ensure_runtime_paths, get_runtime_path
from osa_web.state import keys


def initialize_session(config: dict[str, Any]) -> None:
    ensure_runtime_paths(config)

    if keys.RUNNING not in st.session_state:
        st.session_state[keys.RUNNING] = False
    if keys.CONFIGURATION not in st.session_state:
        st.session_state[keys.CONFIGURATION] = copy.deepcopy(config)
    if keys.TMPDIR not in st.session_state:
        st.session_state[keys.TMPDIR] = tempfile.mkdtemp(
            dir=get_runtime_path(config, "tmp")
        )
    if keys.OUTPUT_REPORT_PATHS not in st.session_state:
        st.session_state[keys.OUTPUT_REPORT_PATHS] = []
    if keys.OUTPUT_REPORT_FILENAMES not in st.session_state:
        st.session_state[keys.OUTPUT_REPORT_FILENAMES] = []
    if keys.GIT_TOKEN not in st.session_state:
        st.session_state[keys.GIT_TOKEN] = os.getenv("GIT_TOKEN")


def current_mode_config() -> dict[str, Any]:
    return st.session_state[keys.CONFIGURATION][st.session_state[keys.MODE_SELECT]]


def reset_run_output() -> None:
    st.session_state[keys.OUTPUT_REPORT_PATHS] = []
    st.session_state[keys.OUTPUT_REPORT_FILENAMES] = []

    for key in (
        keys.OUTPUT_ABOUT_SECTION,
        keys.OUTPUT_EXIT_CODE,
        keys.OUTPUT_MESSAGE,
        keys.OUTPUT_LOGS,
    ):
        if key in st.session_state:
            del st.session_state[key]
