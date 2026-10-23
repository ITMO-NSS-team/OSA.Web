from importlib.metadata import version

import streamlit as st

from osa_web import __version__
from osa_web.auth.state import get_display_name, is_guest_mode


def render_sidebar_element() -> None:
    """Render sidebar with configuration options."""
    with st.sidebar:
        # st.logo("assets/osa_logo.png", size="large")
        username = get_display_name()
        st.markdown(
            f'<h1 style="text-align: center;">Welcome, {username} 👋</h1>',
            unsafe_allow_html=True,
        )
        if is_guest_mode():
            st.warning(
                "Guest mode requires your own provider credentials or a local Ollama server.",
                icon=":material/key:",
            )

        st.divider()

        _, center, _ = st.columns([0.2, 0.6, 0.2])
        with center:
            # TODO: developer only
            # st.write(st.session_state.tmpdirname)
            st.link_button(
                "About OSA",
                url="https://github.com/aimclub/OSA",
                width="stretch",
                icon=":material/info:",
            )
            st.link_button(
                "About Web",
                url="https://github.com/ITMO-NSS-team/OSA.Web",
                width="stretch",
                icon=":material/info:",
            )
            st.container(height=10, border=False)
            st.link_button(
                "Get Help",
                url="https://t.me/osa_helpdesk",
                width="stretch",
                icon=":material/help:",
            )
            st.container(height=10, border=False)
            if is_guest_mode():
                st.button(
                    "Log in",
                    key="sidebar-login",
                    on_click=st.login,
                    args=("aimclub",),
                    width="stretch",
                    type="primary",
                    icon=":material/login:",
                )
            else:
                st.button(
                    "Log out",
                    key="sidebar-logout",
                    on_click=st.logout,
                    width="stretch",
                    type="primary",
                    icon=":material/logout:",
                )

            st.container(height=15, border=False)

            with st.container(horizontal_alignment="center", border=True):
                st.markdown(f"OSA Version: {version('osa_tool')}")
                st.markdown(f"Web Version: {__version__}")

        style = """
            <style>
            button[data-baseweb="tab"] {
            font-size: 24px;
            margin: 0;
            flex: 1;
            justify-content: center;
            }
            section[data-testid="stSidebar"] {
            width: 350px !important;
            }
            .st-key-sidebar-login button,
            .st-key-sidebar-login button *,
            .st-key-sidebar-logout button,
            .st-key-sidebar-logout button * {
            color: #171717 !important;
            }
            </style>
            """
        st.html(style)
