"""Shared console view and replay-friendly download names."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from urllib.parse import urlparse

import streamlit as st


def console_filename(repository_url: str, started_at: datetime | None = None) -> str:
    """Name a captured run after its repository and UTC start time."""
    parts = [part for part in urlparse(repository_url).path.split("/") if part]
    repository = "-".join(parts[:2]) if len(parts) >= 2 else "osa-run"
    slug = re.sub(r"[^a-z0-9_-]+", "-", repository.lower()).strip("-") or "osa-run"
    timestamp = (started_at or datetime.now(UTC)).astimezone(UTC)
    return f"{slug}-{timestamp:%Y%m%d-%H%M%SZ}.txt"


def render_console_output(
    content: str,
    repository_url: str,
    *,
    started_at: datetime | None = None,
    caption: str | None = None,
    expanded: bool = False,
    downloadable: bool = True,
) -> None:
    """Show the same console expander for either live work mode or a replay."""
    with st.expander("See Console Output", expanded=expanded, icon=":material/terminal:"):
        if caption:
            st.caption(caption)
        st.code(content or "Waiting for OSA output...", language="text", height=350)
        if content and downloadable:
            st.download_button(
                "Download console output",
                data=content,
                file_name=console_filename(repository_url, started_at),
                mime="text/plain",
            )
