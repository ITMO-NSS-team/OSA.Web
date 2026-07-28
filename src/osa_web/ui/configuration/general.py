from __future__ import annotations

import streamlit as st

from osa_web.ui.configuration.schema import configuration_callback, current_section


@st.fragment
def render_osa_settings_block() -> None:
    with st.container(border=True):
        st.markdown(
            '<h5 style="text-align: center;">General OSA Settings</h5>',
            unsafe_allow_html=True,
        )
        left, right = st.columns(2)
        current_general = current_section("general")
        with left:
            st.checkbox(
                label="Validate Paper",
                key="configuration-general-validate-paper",
                on_change=configuration_callback,
                args=[
                    "general",
                    "validate-paper",
                    "configuration-general-validate-paper",
                ],
                disabled=current_general["validate-doc"],
                value=current_general["validate-paper"],
                help="""Check whether the experiments proposed in an attached
                    research paper can be reproduced using the selected repository
                    `Default: False`""",
            )
            st.checkbox(
                label="Generate README",
                key="configuration-general-readme",
                on_change=configuration_callback,
                args=["general", "readme", "configuration-general-readme"],
                value=current_general["readme"],
                help="""Generate a `README.md` file based on repository content and metadata
                        `Default: False`""",
            )
            st.checkbox(
                label="Organize Repository",
                key="configuration-general-organize",
                on_change=configuration_callback,
                args=["general", "organize", "configuration-general-organize"],
                value=current_general["organize"],
                help="""Organize the repository by adding standard `tests` and `examples` directories if missing
                        `Default: False`""",
            )
            st.checkbox(
                label="Generate Docstrings",
                key="configuration-general-docstring",
                on_change=configuration_callback,
                args=["general", "docstring", "configuration-general-docstring"],
                value=current_general["docstring"],
                help="""Automatically generate docstrings for all Python files in the repository
                    `Default: False`""",
            )
        with right:
            st.checkbox(
                label="Validate Document",
                key="configuration-general-validate-doc",
                on_change=configuration_callback,
                args=[
                    "general",
                    "validate-doc",
                    "configuration-general-validate-doc",
                ],
                disabled=current_general["validate-paper"],
                value=current_general["validate-doc"],
                help="""Check whether the experiments proposed in an attached
                    documentation file can be reproduced using the selected repository
                    `Default: False`""",
            )
            st.checkbox(
                label="Refine README",
                key="configuration-general-refine-readme",
                on_change=configuration_callback,
                args=[
                    "general",
                    "refine-readme",
                    "configuration-general-refine-readme",
                ],
                value=current_general["refine-readme"],
                help="""Enable advanced README refinement. This process requires a powerful LLM model (such as GPT-4 or equivalent) for optimal results
                        `Default: False`""",
            )
            st.checkbox(
                label="Translate Directories",
                key="configuration-general-translate-dirs",
                on_change=configuration_callback,
                args=[
                    "general",
                    "translate-dirs",
                    "configuration-general-translate-dirs",
                ],
                value=current_general["translate-dirs"],
                help="""Enable automatic translation of directory names into English
                    `Default: False`""",
            )
            st.checkbox(
                label="Generate Requirements",
                key="configuration-general-requirements",
                on_change=configuration_callback,
                args=["general", "requirements", "configuration-general-requirements"],
                value=current_general["requirements"],
                help="""Generate a `requirements.txt` file based on repository content
                    `Default: True`""",
            )
        st.checkbox(
            label="Generate PDF Report",
            key="configuration-general-report",
            on_change=configuration_callback,
            args=["general", "report", "configuration-general-report"],
            value=current_general["report"],
            help="""Analyze the repository and generate a PDF report with project insights
                    `Default: True`""",
        )
        st.checkbox(
            label="Generate About Section",
            key="configuration-general-about",
            on_change=configuration_callback,
            args=["general", "about", "configuration-general-about"],
            value=current_general["about"],
            help="""Generate GitHub `About` section with tags
                    `Default: True`""",
        )
        st.checkbox(
            label="Generate Community Documentation Files",
            key="configuration-general-community-docs",
            on_change=configuration_callback,
            args=["general", "community-docs", "configuration-general-community-docs"],
            value=current_general["community-docs"],
            help="""Generate community-related documentation files,
                    such as `Code of Conduct` and `Contributing guidelines`
                    `Default: False`""",
        )
        st.selectbox(
            label="Ensure License",
            key="configuration-general-ensure-license",
            on_change=configuration_callback,
            args=["general", "ensure-license", "configuration-general-ensure-license"],
            options=(
                None,
                "bsd-3",
                "mit",
                "ap2",
            ),
            index=1,
            help="""
                Enable LICENSE file compilation
                `Default: BSD-3`
                """,
        )
        st.text_input(
            label="Translate README",
            key="configuration-general-translate-readme",
            on_change=configuration_callback,
            args=[
                "general",
                "translate-readme",
                "configuration-general-translate-readme",
            ],
            value=current_general["translate-readme"],
            help="""List of target languages to translate the project's main README into.
                    Each language should be specified by its name (e.g., "Russian", "Chinese").
                    The translated README files will be saved separately in the repository folder
                    with language-specific suffixes (e.g., README_ru.md, README_zh.md).
                    **Example: Russian Chinese**
                    `Default: Russian`""",
        )
        st.text_input(
            label="Convert Notebooks",
            key="configuration-general-convert-notebooks",
            on_change=configuration_callback,
            args=[
                "general",
                "convert-notebooks",
                "configuration-general-convert-notebooks",
            ],
            value=current_general["convert-notebooks"],
            help="""Convert Jupyter notebooks to `.py` format
                    Provide paths, or leave empty for repo directory
                    **Example: path/to/file1 path/to/file2**
                    `Default: -`""",
        )
