import os
import tempfile
from typing import Any

import streamlit as st
import toml
from dotenv import load_dotenv

from configuration_tab import render_configuration_tab
from logger_config import logger
from login_screen import render_login_screen
from main_tab import render_main_tab
from sidebar_element import render_sidebar_element

load_dotenv()

def setup_page_config() -> None:
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_icon=":bee:",
        page_title="OSA Tool",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "About": "https://github.com/ITMO-NSS-team/Open-Source-Advisor",
            "Get Help": "https://t.me/osa_helpdesk",
        },
    )


@st.cache_data
def get_config() -> dict[str, Any]:
    return toml.load("config.toml")


def main() -> None:
    """Run the Streamlit application."""

    setup_page_config()

    if not st.user.is_logged_in:
        render_login_screen()
        st.stop()

    logger.info(f"User {st.user.get("name", "Username")} logged in!")

    if "tmpdirname" not in st.session_state:
        st.session_state.tmpdirname = tempfile.mkdtemp(dir=get_config()["paths"]["tmp"])
        logger.debug(f"Created tmp directory: {st.session_state.tmpdirname}")
    if "git_token" not in st.session_state:
        st.session_state.git_token = os.getenv("GIT_TOKEN")

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
