from __future__ import annotations

import streamlit as st

from osa_web.ui.configuration.schema import configuration_callback, current_section


@st.fragment
def render_workflows_settings_block() -> None:
    with st.container(border=True):
        st.markdown(
            '<h5 style="text-align: center;">Workflow Settings</h5>',
            unsafe_allow_html=True,
        )
        current_workflows = current_section("workflows")
        workflows = st.checkbox(
            label="Generate Workflows",
            key="configuration-workflows-generate-workflows",
            on_change=configuration_callback,
            args=[
                "workflows",
                "generate-workflows",
                "configuration-workflows-generate-workflows",
            ],
            value=current_workflows["generate-workflows"],
            help="""
                Generate GitHub Action workflows for the repository
                `Default: True`""",
        )
        if workflows:
            st.multiselect(
                label="Python Versions",
                key="configuration-workflows-python-versions",
                on_change=configuration_callback,
                args=[
                    "workflows",
                    "python-versions",
                    "configuration-workflows-python-versions",
                ],
                default=current_workflows["python-versions"],
                options=["3.8", "3.9", "3.10", "3.11", "3.12"],
                help="""Python versions to test against
                        `Default: [3.8, 3.9, 3.10]`""",
            )
            st.text_input(
                label="Branches",
                key="configuration-workflows-branches",
                on_change=configuration_callback,
                args=[
                    "workflows",
                    "branches",
                    "configuration-workflows-branches",
                ],
                value=current_workflows["branches"],
                help="""Branches to trigger workflows on
                        **Example: main develop**
                        `Default: -`""",
            )
            st.text_input(
                disabled=True,
                label="Workflow Output Directory",
                help="""Directory where workflow files will be saved
                    **Temporary disabled**
                    `Default: .github/workflows`""",
            )
            left, right = st.columns([0.4, 0.6])
            st.checkbox(
                label="Include Unit Tests",
                key="configuration-workflows-include-tests",
                on_change=configuration_callback,
                args=[
                    "workflows",
                    "include-tests",
                    "configuration-workflows-include-tests",
                ],
                value=current_workflows["include-tests"],
                help="""
                Include unit tests workflow
                `Default: True`""",
            )
            st.checkbox(
                label="Include PyPi",
                key="configuration-workflows-include-pypi",
                on_change=configuration_callback,
                args=[
                    "workflows",
                    "include-pypi",
                    "configuration-workflows-include-pypi",
                ],
                value=current_workflows["include-pypi"],
                help="""Include PyPI publish workflow
                `Default: False`""",
            )
            with left:
                st.checkbox(
                    label="Include codecov",
                    key="configuration-workflows-include-codecov",
                    on_change=configuration_callback,
                    args=[
                        "workflows",
                        "include-codecov",
                        "configuration-workflows-include-codecov",
                    ],
                    value=current_workflows["include-codecov"],
                    help="""
                    Include Codecov coverage step in unit tests workflow
                    `Default: True`""",
                )
                st.checkbox(
                    label="Include Black",
                    key="configuration-workflows-include-black",
                    on_change=configuration_callback,
                    args=[
                        "workflows",
                        "include-black",
                        "configuration-workflows-include-black",
                    ],
                    value=current_workflows["include-black"],
                    help="""
                Include Black formatter workflow
                `Default: True`""",
                )
                st.checkbox(
                    label="Include PEP 8",
                    key="configuration-workflows-include-pep8",
                    on_change=configuration_callback,
                    args=[
                        "workflows",
                        "include-pep8",
                        "configuration-workflows-include-pep8",
                    ],
                    value=current_workflows["include-pep8"],
                    help="""Include PEP 8 compliance workflow
                `Default: True`""",
                )
            with right:
                st.checkbox(
                    label="Use codecov Token",
                    key="configuration-workflows-codecov-token",
                    on_change=configuration_callback,
                    args=[
                        "workflows",
                        "codecov-token",
                        "configuration-workflows-codecov-token",
                    ],
                    value=current_workflows["codecov-token"],
                    help="""
                    Include Use Codecov token for coverage upload
                    `Default: False`""",
                )
                st.checkbox(
                    label="Include autopep8",
                    key="configuration-workflows-include-autopep8",
                    on_change=configuration_callback,
                    args=[
                        "workflows",
                        "include-autopep8",
                        "configuration-workflows-include-autopep8",
                    ],
                    value=current_workflows["include-autopep8"],
                    help="""Include autopep8 formatter workflow
                `Default: False`""",
                )
                st.checkbox(
                    label="Include `/fix-pep8` command",
                    key="configuration-workflows-include-fix-pep8",
                    on_change=configuration_callback,
                    args=[
                        "workflows",
                        "include-fix-pep8",
                        "configuration-workflows-include-fix-pep8",
                    ],
                    value=current_workflows["include-fix-pep8"],
                    help="""Include fix-pep8 command workflow
                `Default: False`""",
                )
            st.selectbox(
                label="PEP8 Tool",
                key="configuration-workflows-pep8-tool",
                on_change=configuration_callback,
                args=[
                    "workflows",
                    "pep8-tool",
                    "configuration-workflows-pep8-tool",
                ],
                options=("flake8", "pylint"),
                help="""
                Tool to use for PEP 8 checking
                `Default: flake8`
                """,
            )
            st.checkbox(
                label="Poetry",
                key="configuration-workflows-use-poetry",
                on_change=configuration_callback,
                args=[
                    "workflows",
                    "use-poetry",
                    "configuration-workflows-use-poetry",
                ],
                value=current_workflows["use-poetry"],
                help="""Use Poetry for packaging
                `Default: False`""",
            )
