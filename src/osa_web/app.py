from typing import Any

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from osa_web.auth.login import render_login_screen
from osa_web.auth.state import get_display_name, is_app_access_allowed, set_user_mode
from osa_web.logging_config import logger
from osa_web.settings import load_config
from osa_web.state import keys
from osa_web.state.session import initialize_session
from osa_web.ui.configuration.page import render_configuration_tab
from osa_web.ui.configuration.schema import reset_configuration_widgets
from osa_web.ui.conversation import render_conversation_tab
from osa_web.ui.home import render_main_tab
from osa_web.ui.sidebar import render_sidebar_element


def setup_page_config() -> None:
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_icon=":honeybee:",
        page_title="OSA.Web",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "About": """OSA Main Repository: https://github.com/aimclub/OSA  
            OSA Web Repository: https://github.com/ITMO-NSS-team/OSA.Web  
            ---  
            Get Help: https://t.me/osa_helpdesk""",
        },
    )


@st.cache_data
def get_config() -> dict[str, Any]:
    return load_config()


def main() -> None:
    """Run the Streamlit application."""

    setup_page_config()

    if getattr(st.user, "is_logged_in", False):
        set_user_mode()

    if not is_app_access_allowed():
        render_login_screen()
        st.stop()

    logger.info(f"User {get_display_name()} logged in!")

    initialize_session(get_config())

    render_sidebar_element()

    st.markdown(
        """
    <style>
    /* Target the tab container */
    [data-testid="stTabs"] [role="tablist"] {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(
        [
            ":material/home: Home",
            ":material/settings: Configuration",
        ],
        key="osa-tabs",
        on_change="rerun",
    )
    if tab1.open:
        with tab1:
            _, center, _ = st.columns([0.1, 0.8, 0.1])
            with center:
                work_mode = st.segmented_control(
                    "Work mode",
                    [keys.WORK_MODE_PIPELINE, keys.WORK_MODE_AGENTIC],
                    default=keys.WORK_MODE_PIPELINE,
                    required=True,
                    key=keys.WORK_MODE,
                    on_change=reset_configuration_widgets,
                    persist_state="session",
                    width="content",
                    help=(
                        "Automated pipeline runs the fast or quality preset. "
                        "Agentic conversation lets agents choose tasks and ask for review. "
                        "`Default: Automated pipeline`"
                    ),
                )
                if work_mode == keys.WORK_MODE_AGENTIC:
                    render_conversation_tab()
            if work_mode == keys.WORK_MODE_PIPELINE:
                render_main_tab()

    if tab2.open:
        with tab2:
            render_configuration_tab()


if __name__ == "__main__":
    main()
