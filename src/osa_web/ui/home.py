import asyncio

import streamlit as st

from osa_web.auth.state import is_guest_mode
from osa_web.osa_tool.runner import run_osa_tool
from osa_web.ui.attachment import render_attachment_block
from osa_web.ui.configuration.schema import reset_configuration_widgets
from osa_web.ui.console_output import render_console_output
from osa_web.ui.publishing_confirmation import render_publishing_confirmation


@st.dialog("Run OSA Tool")
def confirm_public_run() -> None:
    cancelled, confirmed = render_publishing_confirmation(st.session_state.repo_url.strip())
    if cancelled:
        st.rerun()
    if confirmed:
        st.session_state.running = True
        st.rerun()


def render_input_block() -> None:
    st.container(height=5, border=False)
    st.markdown(
        '<h3 style="text-align: center;">To start processing a repository, please enter a GitHub repository URL: </h3>',
        unsafe_allow_html=True,
    )
    st.container(height=5, border=False)
    with st.container(border=True):
        st.text_input(
            label="Repository URL :red[*]",
            key="repo_url",
            disabled=st.session_state.running,
            help="""Enter a GitHub repository URL  
                **Example: https://github.com/aimclub/OSA**""",
            placeholder="https://github.com/aimclub/OSA",
        )
        st.container(height=5, border=False)

        left, right = st.columns(2, gap="medium")
        with left:
            st.selectbox(
                label="Mode",
                key="mode_select",
                options=("quality", "fast"),
                on_change=reset_configuration_widgets,
                persist_state="session",
                disabled=st.session_state.running,
                help="Choose a preset for the automated pipeline. Default: quality.",
            )
            multi_left = """Select the operation mode for repository processing:  
                    - **Fast:** Run a minimal set of essential tasks using efficient model settings.  
                    - **Quality:** Run a comprehensive set of tasks with higher-quality LLM configurations for deeper improvements.
                    """
            st.markdown(multi_left)
        with right:
            render_attachment_block(disabled=st.session_state.running)
            st.markdown(
                "**NOTE**: Recommendations for the Git `About` section will be included in the Pull Request description."
            )


def _set_osa_running():
    git = st.session_state.configuration[st.session_state.mode_select]["git"]
    if not git["no-fork"] or not git["no-pull-request"]:
        confirm_public_run()
    else:
        st.session_state.running = True


def render_button_block() -> None:
    st.container(height=5, border=False)
    guest_provider_blocked = is_guest_mode() and st.session_state.configuration[
        st.session_state.mode_select
    ]["llm"]["api"] in {"itmo", "host"}
    if guest_provider_blocked:
        st.warning("Select OpenAI or Ollama in Configuration before running as a guest.")
    if not st.session_state.git_token:
        st.warning(
            "GIT_TOKEN not found in .env file. The tool may not work correctly with private repositories.",
            icon=":material/warning:",
        )
        st.container(height=5, border=False)
    st.button(
        "Run OSA",
        icon=":material/emoji_nature:",
        width="stretch",
        disabled=st.session_state.running
        or len(st.session_state.repo_url) == 0
        or guest_provider_blocked,
        type="secondary" if len(st.session_state.repo_url) == 0 else "primary",
        on_click=_set_osa_running,
    )


def render_output_block(output_container) -> None:
    with output_container, st.container():
        if "output_logs" in st.session_state:
            st.divider()
            if "output_exit_code" not in st.session_state:
                st.markdown(
                    '<p style="text-align: center;">No output.</p>',
                    unsafe_allow_html=True,
                )
                return
            left, right = st.columns([0.6, 0.4], vertical_alignment="center")
            with left:
                if st.session_state.output_exit_code == 0 and not st.session_state.get(
                    "output_has_errors", False
                ):
                    st.success(
                        st.session_state.output_message,
                        icon=":material/check_circle:",
                    )
                else:
                    st.error(st.session_state.output_message, icon=":material/error:")
            with right:
                if len(st.session_state.output_report_paths) > 0:
                    for i in range(len(st.session_state.output_report_paths)):
                        report_name = st.session_state.output_report_filenames[i]
                        with open(st.session_state.output_report_paths[i], "rb") as file:
                            st.download_button(
                                label=f"Download *`{report_name}`*",
                                data=file,
                                file_name=st.session_state.output_report_filenames[i],
                                mime="application/pdf",
                                icon=":material/download:",
                                width="stretch",
                            )
                else:
                    with st.container(border=True):
                        st.markdown(
                            '<p style="text-align: center;">PDF Report was not created.</p>',
                            unsafe_allow_html=True,
                        )
            if "output_about_section" in st.session_state:
                with st.expander("About section", expanded=True, icon=":material/article:"):
                    st.write(st.session_state.output_about_section)
            render_console_output(
                st.session_state.output_logs,
                st.session_state.repo_url,
                started_at=st.session_state.get("run_started_at"),
                expanded=st.session_state.output_exit_code != 0
                or st.session_state.get("output_has_errors", False),
            )


def render_main_tab() -> None:
    _, center, _ = st.columns([0.1, 0.8, 0.1])
    with center:
        render_input_block()
        render_button_block()
    _, right = st.columns([0.35, 0.5])
    output_container = st.empty()

    if st.session_state.running:
        with right, st.spinner(text="In progress...", show_time=True, width="stretch"):
            asyncio.run(run_osa_tool(output_container))

    render_output_block(output_container)
