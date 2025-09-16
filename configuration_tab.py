import streamlit as st


def configuration_callback(table: str, key: str, value: str):
    st.session_state.configuration[table][key] = st.session_state[value]


@st.fragment
def render_git_settings_block() -> None:
    with st.container(border=True):
        st.markdown(
            '<h5 style="text-align: center;">Git Settings</h5>',
            unsafe_allow_html=True,
        )
        if st.session_state.git_token:
            st.info("**GIT_TOKEN Status**: Found", icon=":material/check_circle:")
        else:
            st.info("**GIT_TOKEN Status**: Found", icon=":material/error:")

        if not st.session_state.git_token:
            st.warning(
                "GIT_TOKEN not found in .env file. Some features may not work correctly."
            )
        st.text_input(
            label="Branch",
            key="configuration-git-branch",
            on_change=configuration_callback,
            args=["git", "branch", "configuration-git-branch"],
            value=st.session_state.configuration["git"]["branch"],
            help="""Branch name of the GitHub repository  
                `Default: Default branch`""",
        )
        left, right = st.columns(2)
        with left:
            st.checkbox(
                label="No pull request",
                key="configuration-git-no-pull-request",
                on_change=configuration_callback,
                args=["git", "no-pull-request", "configuration-git-no-pull-request"],
                value=st.session_state.configuration["git"]["no-pull-request"],
                help="""Avoid create pull request for target repository  
                `Default: False`""",
            )
        with right:
            st.checkbox(
                label="No fork",
                key="configuration-git-no-fork",
                on_change=configuration_callback,
                args=["git", "no-fork", "configuration-git-no-fork"],
                value=st.session_state.configuration["git"]["no-fork"],
                help="""Avoid create fork for target repository  
                        `Default: False`""",
            )


@st.fragment
def render_osa_settings_block() -> None:
    with st.container(border=True):
        st.markdown(
            '<h5 style="text-align: center;">OSA settings</h5>',
            unsafe_allow_html=True,
        )
        st.text_input(
            label="Output",
            value="Current working directory",
            disabled=True,
            help="""Path to the output directory  
                    `Default: Current working directory`""",
        )
        left, right = st.columns(2)
        with left:
            st.checkbox(
                label="Web Mode",
                help="""Enable web interface mode. When set, the tool will generate  
                        the task plan without launching the interactive CLI editor  
                        `Default: False`""",
                value=True,
                disabled=True,
            )
        with right:
            st.checkbox(
                label="Delete directory",
                help="""
                Enable deleting the downloaded repository after processing (Linux only)  
                `Default: False`""",
                value=True,
                disabled=True,
            )
        left, right = st.columns(2)
        with left:
            st.checkbox(
                label="Generate README",
                value=True,
                help="""Generate a `README.md` file based on repository content and metadata  
                        `Default: False`""",
            )
            st.checkbox(
                label="Organize Repository",
                value=True,
                help="""Organize the repository by adding standard `tests` and `examples` directories if missing  
                        `Default: False`""",
            )
            st.checkbox(
                label="Generate Docstrings",
                value=True,
                help="""Automatically generate docstrings for all Python files in the repository  
                    `Default: False`""",
            )
        with right:
            st.checkbox(
                label="Refine README",
                value=False,
                help="""Enable advanced README refinement. This process requires a powerful LLM model (such as GPT-4 or equivalent) for optimal results  
                        `Default: False`""",
            )
            st.checkbox(
                label="Translate Directories",
                help="""Enable automatic translation of directory names into English  
                    `Default: False`""",
            )
            st.checkbox(
                label="Generate Requirements",
                value=False,
                help="""Generate a `requirements.txt` file based on repository content  
                    `Default: False`""",
            )
        st.checkbox(
            label="Generate PDF Report",
            value=True,
            help="""Analyze the repository and generate a PDF report with project insights  
                    `Default: False`""",
        )
        st.checkbox(
            label="Generate About Section",
            value=True,
            help="""Generate GitHub `About` section with tags  
                    `Default: False`""",
        )
        st.checkbox(
            label="Generate Community Documentation Files",
            value=True,
            help="""Generate community-related documentation files,  
                    such as `Code of Conduct` and `Contributing guidelines`  
                    `Default: False`""",
        )
        st.multiselect(
            "Convert Notebooks",
            [],
            accept_new_options=True,
            help="""Convert Jupyter notebooks to `.py` format  
                    Provide paths, or leave empty for repo directory  
                    **Example: path/to/file1, path/to/file2**  
                    `Default: —`""",
        )
        st.selectbox(
            label="Ensure License",
            options=(None, "bsd-3", "mit", "ap2"),
            help="""
                Enable LICENSE file compilation  
                `Default: None`
                """,
        )


@st.fragment
def render_workflow_settings_block() -> None:
    with st.container(border=True):
        st.markdown(
            '<h5 style="text-align: center;">Workflow settings</h5>',
            unsafe_allow_html=True,
        )
        workflows = st.checkbox(
            label="Generate Workflows",
            help="""
                Generate GitHub Action workflows for the repository  
                `Default: False`""",
            value=False,
        )
        if workflows:
            st.multiselect(
                label="Python Verisons",
                default=["3.9", "3.10"],
                options=["3.9", "3.10", "3.11", "3.12"],
                help="""Python versions to test against
                        `Default: [3.9, 3.10]`""",
            )
            st.multiselect(
                label="Branches",
                options=[],
                accept_new_options=True,
                help="""Branches to trigger workflows on
                        `Default: []`""",
            )
            st.text_input(
                label="Workflow Output Directory",
                value=".github/workflows",
                help="""Directory where workflow files will be saved  
                    `Default: .github/workflows`""",
            )
            left, right = st.columns([0.4, 0.6])
            st.checkbox(
                label="Include Unit Tests",
                help="""
                Include unit tests workflow  
                `Default: True`""",
                value=True,
            )
            st.checkbox(
                label="Include PyPi",
                help="""Include PyPI publish workflow  
                `Default: False`""",
                value=False,
            )
            with left:
                st.checkbox(
                    label="Include codecov",
                    help="""
                    Include Codecov coverage step in unit tests workflow  
                    `Default: True`""",
                    value=True,
                )
                st.checkbox(
                    label="Include Black",
                    help="""
                Include Black formatter workflow  
                `Default: True`""",
                    value=True,
                )
                st.checkbox(
                    label="Include PEP 8",
                    help="""Include PEP 8 compliance workflow  
                `Default: True`""",
                    value=True,
                )
            with right:
                st.checkbox(
                    label="Use codecov Token",
                    help="""
                    Include Use Codecov token for coverage upload  
                    `Default: False`""",
                    value=False,
                )
                st.checkbox(
                    label="Include autopep8",
                    help="""Include autopep8 formatter workflow  
                `Default: False`""",
                    value=False,
                )
                st.checkbox(
                    label="Include `/fix-pep8` command",
                    help="""Include fix-pep8 command workflow  
                `Default: False`""",
                    value=False,
                )
            st.selectbox(
                label="PEP8 Tool",
                options=("flake8", "pylint"),
                help="""
                Tool to use for PEP 8 checking  
                `Default: flake8`
                """,
            )


@st.fragment
def render_llm_settings_block() -> None:
    with st.container(border=True):
        st.markdown(
            '<h5 style="text-align: center;">LLM settings</h5>',
            unsafe_allow_html=True,
        )
        st.selectbox(
            label="API",
            options=("itmo (Gemma-3-27b)", "llama", "openai", "ollama"),
            help="""
                LLM API service provider  
                `Default: llama`
                """,
        )
        st.text_input(
            label="Base URL",
            value="https://api.openai.com/v1",
            help="""
                URL of the provider compatible with OpenAI API  
                `Default: https://api.openai.com/v1`""",
        )
        st.text_input(
            label="Model",
            value="gpt-3.5-turbo",
            help="""
                Specific LLM model to use  
                `Default: gpt-3.5-turbo`  
                See:
                1. https://vsegpt.ru/Docs/Models  
                2. https://platform.openai.com/docs/models  
                3. https://ollama.com/library  """,
        )
        st.number_input(
            label="Maximum number of tokens",
            value=4096,
            help="""
                Maximum number of tokens the model can generate in a single response  
                **Example: 1024**  
                `Default: 4096`""",
        )
        st.selectbox(
            label="Temperature",
            options=(None, 0, 1),
            help="""
                Sampling temperature to use for the LLM output (0 = deterministic, 1 = creative)  
                `Default: None`""",
        )
        st.number_input(
            label="Top-p (Nucleus Sampling)",
            value=None,
            help="""
                Nucleus sampling probability (1.0 = all tokens considered)  
                *Example: 0.8**  
                `Default: None`""",
        )


def render_configuration_tab() -> None:
    left, center, right = st.columns([1, 1, 1])
    with left:
        render_git_settings_block()
        render_osa_settings_block()
    with center:
        render_workflow_settings_block()
    with right:
        render_llm_settings_block()
