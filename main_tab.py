import asyncio
import tempfile

import streamlit as st

from logger_config import logger
from utils import run_osa_tool


def reset_article_selection() -> None:
    st.session_state.article_selection_pills = None


@st.dialog("Add an Article", on_dismiss=reset_article_selection)
def add_article(type) -> None:
    article = None
    if type == "URL":
        article = st.text_input("Paste URL")
    elif type == "File":
        article = st.file_uploader("Upload Article", ["pdf"])

    st.container(height=5, border=False)

    if st.button(
        "Submit",
        disabled=not article,
        use_container_width=True,
        type="primary",
        help="""Select a README template for a repository with an article.
    Or provide a link to the pdf file""",
    ):
        if type == "File":
            tmpfilename = tempfile.NamedTemporaryFile(
                delete=False, dir=st.session_state.tmpdirname, suffix=".pdf"
            )
            tmpfilename.write(article.getvalue())
            article = tmpfilename.name
        st.session_state.article = {"data": article, "type": type}
        logger.info(f"Added article: {article}")
        st.rerun()


def render_article_block() -> None:
    help_text = """Select a README template for a repository with an article  
                    or provide a link to the PDF file  
                    `Default: None`"""
    if "article" not in st.session_state:
        option_map = {
            "URL": ":material/globe: Paste URL",
            "File": ":material/upload_file: Upload Article",
        }
        selection = st.pills(
            "Article",
            key="article_selection_pills",
            options=option_map.keys(),
            format_func=lambda option: option_map[option],
            selection_mode="single",
            disabled=st.session_state.running,
            help=help_text,
            width="stretch",
        )
        if selection:
            add_article(selection)
    else:
        st.caption("Article", help=help_text)
        st.write(
            f"Article added via **{st.session_state.article.get('type')}**: `{st.session_state.article.get('data')}`"
        )
        if st.button(":material/delete: Remove", use_container_width=True):
            del st.session_state["article"]
            st.rerun()


def render_input_block() -> None:
    st.container(height=5, border=False)
    st.markdown(
        f'<h3 style="text-align: center;">To start processing a repository, please enter a GitHub repository URL: </h3>',
        unsafe_allow_html=True,
    )
    st.container(height=5, border=False)
    with st.container(border=True):
        st.text_input(
            label="Repository URL",
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
                options=("basic", "advanced"),  # "auto"
                disabled=st.session_state.running,
                help="""
                    Operation mode for repository processing  
                    `Default: auto`
                    """,
            )
            multi = """Select the operation mode for repository processing:  
                        - **Basic:** *run a minimal predefined set of tasks;*  
                        - **Auto**: *automatically determine necessary actions based on repository analysis;*  
                        - **Advanced**: *run all enabled features based on a provided configuration.*  
                    """
            st.markdown(multi)
        with right:
            render_article_block()


def _set_osa_running():
    st.session_state.running = True


def render_button_block() -> None:
    st.container(height=5, border=False)
    if not st.session_state.git_token:
        st.warning(
            "GIT_TOKEN not found in .env file. The tool may not work correctly with private repositories.",
            icon=":material/warning:",
        )
        st.container(height=5, border=False)
    st.button(
        "Run OSA",
        icon=":material/emoji_nature:",
        use_container_width=True,
        disabled=st.session_state.running or len(st.session_state.repo_url) == 0,
        type="secondary" if len(st.session_state.repo_url) == 0 else "primary",
        on_click=_set_osa_running,
    )


def render_output_block(output_container) -> None:
    with output_container:
        with st.container():
            if "output_logs" in st.session_state:
                st.divider()
                if "output_exit_code" not in st.session_state:
                    st.markdown(
                        f'<p style="text-align: center;">No output.</p>',
                        unsafe_allow_html=True,
                    )
                    return
                left, right = st.columns([0.8, 0.2], vertical_alignment="center")
                with left:
                    if st.session_state.output_exit_code == 0:
                        st.success(
                            st.session_state.output_message,
                            icon=":material/check_circle:",
                        )
                    else:
                        st.error(
                            st.session_state.output_message, icon=":material/error:"
                        )
                with right:
                    if "output_report_path" in st.session_state:
                        with open(st.session_state.output_report_path, "rb") as file:
                            st.download_button(
                                label="Download Report",
                                data=file,
                                file_name=st.session_state.output_report_filename,
                                mime="application/pdf",
                                icon=":material/download:",
                                use_container_width=True,
                            )
                    else:
                        with st.container(border=True):
                            st.markdown(
                                f'<p style="text-align: center;">PDF Report was not created.</p>',
                                unsafe_allow_html=True,
                            )
                if "output_about_section" in st.session_state:
                    with st.expander(
                        "About section", expanded=True, icon=":material/article:"
                    ):
                        st.write(st.session_state.output_about_section)
                # TODO: developer only
                with st.expander("See Console Output", icon=":material/terminal:"):
                    st.code(
                        st.session_state.output_logs,
                        height=350,
                    )


def render_main_tab() -> None:
    _, center, _ = st.columns([0.1, 0.8, 0.1])
    with center:
        render_input_block()
        render_button_block()
    _, right = st.columns([0.35, 0.5])
    output_container = st.empty()

    if st.session_state.running:
        with right:
            with st.spinner(text="In progress...", show_time=True, width="stretch"):
                asyncio.run(run_osa_tool(output_container))

    render_output_block(output_container)
