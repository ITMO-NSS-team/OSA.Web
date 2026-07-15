import streamlit as st

from osa_web.auth.state import set_guest_mode
from osa_web.settings import asset_path


def render_login_screen() -> None:
    """Render application login screen."""
    _, center, _ = st.columns(3)
    with center:

        _, center, _ = st.columns([0.1, 0.8, 0.1])

        with center:
            st.image(
                str(asset_path("osa_web_logo.png")),
                use_container_width=True,
            )
            st.container(height=20, border=False)

        with st.container(border=True, horizontal_alignment="center"):
            st.markdown(
                '<h2 style="text-align: center;">Sign in to OSA.Web</h2>',
                unsafe_allow_html=True,
            )

            st.container(height=10, border=False)

            with st.container(width=300):
                if st.button(
                    "Log in with AimClub",
                    use_container_width=True,
                    type="primary",
                ):
                    st.login("aimclub")
                st.button(
                    "Continue as guest",
                    use_container_width=True,
                    on_click=set_guest_mode,
                )
                # if st.button("Log in with Google", use_container_width=True):
                #     st.login("google")

            st.container(height=5, border=False)

            st.markdown(
                '<p style="text-align: center; color: grey;">Choose an account sign-in or continue as a guest.</p>',
                unsafe_allow_html=True,
            )

        st.container(height=5, border=False)

        st.markdown(
            '<h6 style="text-align: center;">Created by ITMO with ❤️</h6>',
            unsafe_allow_html=True,
        )
