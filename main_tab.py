import asyncio
import tempfile

import streamlit as st

from utils import run_osa_tool


@st.dialog("Add an Article")
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
        st.rerun()


@st.fragment
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
            options=option_map.keys(),
            format_func=lambda option: option_map[option],
            selection_mode="single",
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
    st.markdown(
        f'<h3 style="text-align: center;">To start processing a repository, please enter a GitHub repository URL: </h3>',
        unsafe_allow_html=True,
    )
    st.text_input(
        label="Repository URL",
        key="repo_url",
        help="""Enter a GitHub repository URL  
            **Example: https://github.com/aimclub/OSA**""",
        placeholder="https://github.com/aimclub/OSA",
    )
    st.container(height=5, border=False)

    left, right = st.columns(2, gap="large")
    with left:
        st.selectbox(
            label="Mode",
            key="mode_select",
            options=("basic", "auto", "advanced"),
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
    st.container(height=5, border=False)


@st.fragment
def render_run_block(output_container) -> None:
    if "run_osa_button" in st.session_state and st.session_state.run_osa_button == True:
        st.session_state.running = True
    else:
        st.session_state.running = False
    if st.button(
        "Run OSA",
        icon=":material/emoji_nature:",
        use_container_width=True,
        disabled=len(st.session_state.repo_url) == 0 or st.session_state.running,
        type="secondary" if len(st.session_state.repo_url) == 0 else "primary",
        key="run_osa_button",
    ):
        if not st.session_state.git_token:
            st.warning(
                "GIT_TOKEN not found in .env file. The tool may not work correctly with private repositories."
            )
        _, right = st.columns([0.35, 0.5])
        with right:
            with st.spinner(text="In progress...", show_time=True, width="stretch"):
                asyncio.run(run_osa_tool(output_container))
            st.rerun()


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
    output_container = st.empty()
    with center:
        render_run_block(output_container)
    render_output_block(output_container)
