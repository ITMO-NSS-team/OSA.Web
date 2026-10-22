"""Attachment picker shared by the automated and agentic workflows."""

from __future__ import annotations

import tempfile
from pathlib import Path
from urllib.parse import urlsplit

import streamlit as st

from osa_web.logging_config import logger
from osa_web.state import keys


def reset_attachment_selection() -> None:
    for selection_key in (
        "attachment_selection_pills",
        "chat_attachment_selection_pills",
        f"{keys.CHAT_ATTACHMENT}-dialog-source",
    ):
        if selection_key in st.session_state:
            st.session_state[selection_key] = None


@st.dialog("Add an attachment", on_dismiss=reset_attachment_selection)
def add_attachment(source: str, state_key: str) -> None:
    attachment = None
    if source == "URL":
        attachment = st.text_input(
            "Paste URL",
            key=f"{state_key}-url",
            help="Public PDF or DOCX URL. Default: no attachment.",
        )
    elif source == "File":
        attachment = st.file_uploader(
            "Upload attachment",
            ["pdf", "docx"],
            key=f"{state_key}-upload",
            help="Choose one PDF or DOCX file. Default: no attachment.",
        )

    st.container(height=5, border=False)
    if st.button(
        "Submit",
        key=f"{state_key}-submit",
        disabled=not attachment,
        width="stretch",
        type="primary",
        help="Attach the selected URL or file to this workflow. Default: none.",
    ):
        if source == "URL":
            parsed = urlsplit(attachment.strip())
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                st.error("Enter a public URL starting with http:// or https://.")
                return
            data = attachment.strip()
        else:
            with tempfile.NamedTemporaryFile(
                delete=False,
                dir=st.session_state[keys.TMPDIR],
                suffix=Path(attachment.name).suffix.lower(),
            ) as file:
                file.write(attachment.getvalue())
                data = file.name
        st.session_state[state_key] = {"data": data, "type": source}
        st.session_state.pop(f"{state_key}-dialog-source", None)
        logger.info("Added %s attachment", source)
        st.rerun()


def render_attachment_block(
    state_key: str = keys.ATTACHMENT,
    *,
    disabled: bool = False,
    full_width_buttons: bool = False,
) -> None:
    help_text = "Select one PDF or DOCX file, or a public URL. Default: no attachment."
    attachment = st.session_state.get(state_key)
    if attachment is None:
        if full_width_buttons:
            dialog_source_key = f"{state_key}-dialog-source"
            st.caption("Attachment", help=help_text)
            url_column, file_column = st.columns(2, gap="small")
            with url_column:
                if st.button(
                    "Paste URL",
                    key=f"{state_key}-choose-url",
                    icon=":material/globe:",
                    width="stretch",
                    disabled=disabled,
                    help=help_text,
                ):
                    st.session_state[dialog_source_key] = "URL"
            with file_column:
                if st.button(
                    "Upload attachment",
                    key=f"{state_key}-choose-file",
                    icon=":material/upload_file:",
                    width="stretch",
                    disabled=disabled,
                    help=help_text,
                ):
                    st.session_state[dialog_source_key] = "File"
            if source := st.session_state.get(dialog_source_key):
                add_attachment(source, state_key)
            return
        option_map = {
            "URL": ":material/globe: Paste URL",
            "File": ":material/upload_file: Upload attachment",
        }
        selection_key = (
            "attachment_selection_pills"
            if state_key == keys.ATTACHMENT
            else "chat_attachment_selection_pills"
        )
        selection = st.pills(
            "Attachment",
            key=selection_key,
            options=option_map.keys(),
            format_func=lambda option: option_map[option],
            selection_mode="single",
            disabled=disabled,
            help=help_text,
            width="stretch",
        )
        if selection:
            add_attachment(selection, state_key)
    else:
        st.caption("Attachment", help=help_text)
        st.write(f"Attachment added via **{attachment['type']}**: `{attachment['data']}`")
        if st.button(
            ":material/delete: Remove",
            key=f"{state_key}-remove",
            width="stretch",
            disabled=disabled,
            help="Remove this attachment. Default: no attachment.",
        ):
            del st.session_state[state_key]
            reset_attachment_selection()
            st.rerun()
