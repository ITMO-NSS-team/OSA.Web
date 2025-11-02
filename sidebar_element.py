import streamlit as st


def render_sidebar_element() -> None:
    """Render sidebar with configuration options."""
    with st.sidebar:
        # st.logo("assets/osa_logo.png", size="large")
        username = st.user.get("name", "Username")
        st.markdown(
            f'<h1 style="text-align: center;">Welcome, {username} 👋</h1>',
            unsafe_allow_html=True,
        )

        st.divider()

        _, center, _ = st.columns([0.2, 0.6, 0.2])
        with center:
            # TODO: developer only
            # st.write(st.session_state.tmpdirname)
            st.link_button(
                "About",
                url="https://github.com/ITMO-NSS-team/Open-Source-Advisor",
                use_container_width=True,
                icon=":material/info:",
            )
            st.link_button(
                "Get Help",
                url="https://t.me/osa_helpdesk",
                use_container_width=True,
                icon=":material/help:",
            )
            st.container(height=10, border=False)
            st.button(
                "Log out",
                on_click=st.logout,
                use_container_width=True,
                type="primary",
                icon=":material/logout:",
            )

            st.container(height=15, border=False)

            with st.container(border=True):
                st.markdown(
                    f"""
                    :grey[OSA Version: v{st.session_state.configuration["versions"]["osa_tool"]}]  
                    :grey[Web Version: v{st.session_state.configuration["versions"]["osa_web"]}]
                    """
                )

        style = """
            <style>
            button[data-baseweb="tab"] {
            font-size: 24px;
            margin: 0;
            width: 100%;
            }
            section[data-testid="stSidebar"] {
            width: 350px !important;
            }
            </style>
            """
        st.write(style, unsafe_allow_html=True)
