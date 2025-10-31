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
            st.warning(
                "**GIT_TOKEN** not found in .env file. Some features may not work correctly.",
                icon=":material/warning:",
            )

        st.text_input(
            label="Branch",
            key="configuration-git-branch",
            on_change=configuration_callback,
            args=["git", "branch", "configuration-git-branch"],
            value=st.session_state.configuration["git"]["branch"],
            help="""Branch name of the GitHub repository  
                `Default: Default repository branch`""",
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
            '<h5 style="text-align: center;">General OSA Settings</h5>',
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
                key="configuration-general-readme",
                on_change=configuration_callback,
                args=["general", "readme", "configuration-general-readme"],
                value=st.session_state.configuration["general"]["readme"],
                help="""Generate a `README.md` file based on repository content and metadata  
                        `Default: False`""",
            )
            st.checkbox(
                label="Organize Repository",
                key="configuration-general-organize",
                on_change=configuration_callback,
                args=["general", "organize", "configuration-general-organize"],
                value=st.session_state.configuration["general"]["organize"],
                help="""Organize the repository by adding standard `tests` and `examples` directories if missing  
                        `Default: False`""",
            )
            st.checkbox(
                label="Generate Docstrings",
                key="configuration-general-docstring",
                on_change=configuration_callback,
                args=["general", "docstring", "configuration-general-docstring"],
                value=st.session_state.configuration["general"]["docstring"],
                help="""Automatically generate docstrings for all Python files in the repository  
                    `Default: False`""",
            )
        with right:
            st.checkbox(
                label="Refine README",
                key="configuration-general-refine-readme",
                on_change=configuration_callback,
                args=[
                    "general",
                    "refine-readme",
                    "configuration-general-refine-readme",
                ],
                value=st.session_state.configuration["general"]["refine-readme"],
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
                value=st.session_state.configuration["general"]["translate-dirs"],
                help="""Enable automatic translation of directory names into English  
                    `Default: False`""",
            )
            st.checkbox(
                label="Generate Requirements",
                key="configuration-general-requirements",
                on_change=configuration_callback,
                args=["general", "requirements", "configuration-general-requirements"],
                value=st.session_state.configuration["general"]["requirements"],
                help="""Generate a `requirements.txt` file based on repository content  
                    `Default: False`""",
            )
        st.checkbox(
            label="Generate PDF Report",
            key="configuration-general-report",
            on_change=configuration_callback,
            args=["general", "report", "configuration-general-report"],
            value=st.session_state.configuration["general"]["report"],
            help="""Analyze the repository and generate a PDF report with project insights  
                    `Default: False`""",
        )
        st.checkbox(
            label="Generate About Section",
            key="configuration-general-about",
            on_change=configuration_callback,
            args=["general", "about", "configuration-general-about"],
            value=st.session_state.configuration["general"]["about"],
            help="""Generate GitHub `About` section with tags  
                    `Default: False`""",
        )
        st.checkbox(
            label="Generate Community Documentation Files",
            key="configuration-general-community-docs",
            on_change=configuration_callback,
            args=["general", "community-docs", "configuration-general-community-docs"],
            value=st.session_state.configuration["general"]["community-docs"],
            help="""Generate community-related documentation files,  
                    such as `Code of Conduct` and `Contributing guidelines`  
                    `Default: False`""",
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
            value=st.session_state.configuration["general"]["convert-notebooks"],
            help="""Convert Jupyter notebooks to `.py` format  
                    Provide paths, or leave empty for repo directory  
                    **Example: path/to/file1, path/to/file2**  
                    `Default: —`""",
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
            value=st.session_state.configuration["general"]["translate-readme"],
            help="""List of target languages to translate the project's main README into.  
                    Each language should be specified by its name (e.g., "Russian", "Chinese").  
                    The translated README files will be saved separately in the repository folder  
                    with language-specific suffixes (e.g., README_ru.md, README_zh.md).  
                    **Example: Russian Chinese**  
                    `Default: —`""",
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
            help="""
                Enable LICENSE file compilation  
                `Default: None`
                """,
        )


@st.fragment
def render_workflows_settings_block() -> None:
    with st.container(border=True):
        st.markdown(
            '<h5 style="text-align: center;">Workflow Settings</h5>',
            unsafe_allow_html=True,
        )
        workflows = st.checkbox(
            label="Generate Workflows",
            key="configuration-workflows-generate-workflows",
            on_change=configuration_callback,
            args=[
                "workflows",
                "generate-workflows",
                "configuration-workflows-generate-workflows",
            ],
            value=st.session_state.configuration["workflows"]["generate-workflows"],
            help="""
                Generate GitHub Action workflows for the repository  
                `Default: False`""",
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
                default=st.session_state.configuration["workflows"]["python-versions"],
                options=["3.8", "3.9", "3.10", "3.11", "3.12"],
                help="""Python versions to test against
                        `Default: [3.8, 3.9, 3.10]`""",
            )
            st.multiselect(
                label="Branches",
                options=st.session_state.configuration["workflows"]["branches"],
                accept_new_options=True,
                help="""Branches to trigger workflows on
                        `Default: []`""",
            )
            st.text_input(
                label="Workflow Output Directory",
                key="configuration-workflows-workflows-output-dir",
                on_change=configuration_callback,
                args=[
                    "workflows",
                    "workflows-output-dir",
                    "configuration-workflows-workflows-output-dir",
                ],
                value=st.session_state.configuration["workflows"][
                    "workflows-output-dir"
                ],
                help="""Directory where workflow files will be saved  
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
                value=st.session_state.configuration["workflows"]["include-tests"],
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
                value=st.session_state.configuration["workflows"]["include-pypi"],
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
                    value=st.session_state.configuration["workflows"][
                        "include-codecov"
                    ],
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
                    value=st.session_state.configuration["workflows"]["include-black"],
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
                    value=st.session_state.configuration["workflows"]["include-pep8"],
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
                    value=st.session_state.configuration["workflows"]["codecov-token"],
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
                    value=st.session_state.configuration["workflows"][
                        "include-autopep8"
                    ],
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
                    value=st.session_state.configuration["workflows"][
                        "include-fix-pep8"
                    ],
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
                value=st.session_state.configuration["workflows"]["use-poetry"],
                help="""Use Poetry for packaging 
                `Default: False`""",
            )


@st.fragment
def render_llm_settings_block() -> None:
    with st.container(border=True):
        st.markdown(
            '<h5 style="text-align: center;">LLM Settings</h5>',
            unsafe_allow_html=True,
        )
        llm_api_options = ("itmo", "llama", "openai", "ollama")
        st.selectbox(
            label="API",
            key="configuration-llm-api",
            on_change=configuration_callback,
            args=["llm", "api", "configuration-llm-api"],
            index=(
                llm_api_options.index(st.session_state.configuration["llm"]["api"])
                if "api" in st.session_state.configuration["llm"]
                else 0
            ),
            options=llm_api_options,
            help="""
                LLM API service provider  
                `Default: itmo (Gemma-3-27b)`
                """,
        )
        if st.session_state.configuration["llm"]["api"] != "itmo":
            st.text_input(
                label="API Key :red-background[**WARNING**: PLEASE USE THROWAWAY KEYS]",
                key="configuration-api-key",
                type="password",
                help="""
                    Your OpenAI API Key  
                    **Please, refer to [Security Tips.](https://blog.streamlit.io/8-tips-for-securely-using-api-keys/)**
                    """,
            )
            st.text_input(
                label="Base URL",
                key="configuration-base-url",
                on_change=configuration_callback,
                args=["llm", "base-url", "configuration-base-url"],
                value=st.session_state.configuration["llm"]["base-url"],
                help="""
                    URL of the provider compatible with OpenAI API  
                    `Default: https://api.openai.com/v1`""",
            )
            st.text_input(
                label="Model",
                value=st.session_state.configuration["llm"]["model"],
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
            key="configuration-llm-max-tokens",
            on_change=configuration_callback,
            args=["llm", "max-tokens", "configuration-llm-max-tokens"],
            value=st.session_state.configuration["llm"]["max-tokens"],
            help="""
                Maximum number of tokens the model can generate in a single response  
                **Example: 1024**  
                `Default: 4096`""",
        )
        st.selectbox(
            label="Temperature",
            key="configuration-llm-temperature",
            on_change=configuration_callback,
            args=["llm", "temperature", "configuration-llm-temperature"],
            options=(st.session_state.configuration["llm"]["temperature"], 0, 1),
            help="""
                Sampling temperature to use for the LLM output (0 = deterministic, 1 = creative)  
                `Default: None`""",
        )
        st.number_input(
            label="Top-p (Nucleus Sampling)",
            key="configuration-llm-top-p",
            on_change=configuration_callback,
            args=["llm", "top-p", "configuration-llm-top-p"],
            value=st.session_state.configuration["llm"]["top-p"],
            help="""
                Nucleus sampling probability (1.0 = all tokens considered)  
                *Example: 0.8**  
                `Default: None`""",
        )


@st.fragment
def render_only_basic_mode() -> None:
    with st.container(border=True):
        st.markdown(
            f'<h5 style="text-align: center;">Extra Settings</h5>',
            unsafe_allow_html=True,
        )
        st.write("The rest of the settings are only available in `Advanced` mode.")


def render_configuration_tab() -> None:
    left, center, right = st.columns([1, 1, 1])
    if st.session_state.mode_select not in ["basic", "auto"]:
        with left:
            render_git_settings_block()
            render_osa_settings_block()
        with center:
            render_workflows_settings_block()
        with right:
            render_llm_settings_block()
    else:
        with center:
            render_git_settings_block()
            render_only_basic_mode()
