from typing import Any

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from osa_web.auth.login import render_login_screen
from osa_web.auth.state import get_display_name, is_app_access_allowed, set_user_mode
from osa_web.logging_config import logger
from osa_web.settings import load_config
from osa_web.state.session import initialize_session
from osa_web.ui.configuration.page import render_configuration_tab
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

    tab1, tab2 = st.tabs(
        [
            ":material/home: Home",
            ":material/settings: Configuration",
        ]
    )
    with tab1:
        render_main_tab()

    with tab2:
        render_configuration_tab()


if __name__ == "__main__":
    main()
