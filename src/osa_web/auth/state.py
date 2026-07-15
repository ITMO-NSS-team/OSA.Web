from __future__ import annotations

import streamlit as st

GUEST_AUTH_MODE = "guest"
USER_AUTH_MODE = "user"


def is_guest_mode() -> bool:
    return st.session_state.get("auth_mode") == GUEST_AUTH_MODE


def is_app_access_allowed() -> bool:
    return bool(getattr(st.user, "is_logged_in", False)) or is_guest_mode()


def set_guest_mode() -> None:
    st.session_state.auth_mode = GUEST_AUTH_MODE


def set_user_mode() -> None:
    st.session_state.auth_mode = USER_AUTH_MODE


def get_display_name() -> str:
    if is_guest_mode():
        return "Guest"
    if getattr(st.user, "is_logged_in", False):
        return st.user.get("name", "Username")
    return "Username"

