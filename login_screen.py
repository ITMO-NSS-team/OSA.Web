import streamlit as st


def render_login_screen() -> None:
    """Render application login screen."""
    _, center, _ = st.columns(3)
    with center:

        _, center, _ = st.columns([0.1, 0.8, 0.1])

        with center:
            st.image(
                "assets/osa_logo.png",
                use_container_width=True,
            )
            st.container(height=20, border=False)

        with st.container(border=True, height=250):
            st.markdown(
                '<h2 style="text-align: center;">Sign in to OSA</h2>',
                unsafe_allow_html=True,
            )

            with st.container(border=True):
                if st.button(
                    "Log in with AimClub",
                    use_container_width=True,
                    type="primary",
                ):
                    st.login("aimclub")
                if st.button(
                    "Log in with Google", use_container_width=True, disabled=True
                ):
                    st.login("google")

        st.markdown(
            '<h6 style="text-align: center;">Created by ITMO with ❤️</h6>',
            unsafe_allow_html=True,
        )
