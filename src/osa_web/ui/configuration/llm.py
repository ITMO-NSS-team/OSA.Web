from __future__ import annotations

from urllib.parse import urlsplit

import streamlit as st

from osa_web.auth.state import is_guest_mode
from osa_web.state import keys
from osa_web.ui.configuration.schema import (
    configuration_callback,
    current_section,
    selected_configuration_mode,
)


@st.fragment
def render_llm_settings_block() -> None:
    with st.container(border=True):
        st.markdown(
            '<h5 style="text-align: center;">LLM Settings</h5>',
            unsafe_allow_html=True,
        )
        current_llm = current_section("llm")
        default_model = "gpt-6-sol" if selected_configuration_mode() == "quality" else "gpt-6-luna"
        api_key_widget = (
            keys.CONFIGURATION_AGENTIC_API_KEY
            if selected_configuration_mode() == "agentic"
            else keys.CONFIGURATION_API_KEY
        )
        if is_guest_mode():
            if current_llm["api"] in {"itmo", "host", "llama"}:
                current_llm.update(
                    {
                        "api": "openai",
                        "base-url": "https://api.openai.com/v1",
                        "model": default_model,
                    }
                )
            llm_api_options = ("openai", "ollama")
            st.selectbox(
                label="API",
                key="configuration-llm-api",
                on_change=configuration_callback,
                args=["llm", "api", "configuration-llm-api"],
                index=llm_api_options.index(current_llm["api"]),
                options=llm_api_options,
                help="""
                    LLM API service provider
                    `Default: openai`
                    """,
            )
            st.text_input(
                label="API Key :red[*] :red-background[**WARNING**: PLEASE USE THROWAWAY KEYS]",
                key=api_key_widget,
                type="password",
                persist_state="session",
                help="""
                    Provider API key. Default: no key.
                    **Please, refer to [Security Tips.](https://blog.streamlit.io/8-tips-for-securely-using-api-keys/)**
                    """,
            )
            st.text_input(
                label="Base URL",
                key="configuration-base-url",
                on_change=configuration_callback,
                args=["llm", "base-url", "configuration-base-url"],
                value=current_llm["base-url"],
                help="Provider service URL. Default: https://api.openai.com/v1.",
            )
        else:
            if current_llm["api"] == "llama":
                current_llm["api"] = "ollama"
            llm_api_options = ("itmo", "openai", "ollama", "host")
            st.selectbox(
                label="API",
                key="configuration-llm-api",
                on_change=configuration_callback,
                args=["llm", "api", "configuration-llm-api"],
                index=(
                    llm_api_options.index(current_llm["api"])
                    if "api" in current_llm and current_llm["api"] in llm_api_options
                    else 0
                ),
                options=llm_api_options,
                help="""
                    LLM API service provider
                    `Default: openai`
                    """,
            )
            if current_llm["api"] != "itmo":
                st.text_input(
                    label="API Key :red-background[**WARNING**: PLEASE USE THROWAWAY KEYS]",
                    key=api_key_widget,
                    type="password",
                    persist_state="session",
                    help="""
                        Provider API key. Default: no key.
                        **Please, refer to [Security Tips.](https://blog.streamlit.io/8-tips-for-securely-using-api-keys/)**
                        """,
                )
                st.text_input(
                    label="Base URL",
                    key="configuration-base-url",
                    on_change=configuration_callback,
                    args=["llm", "base-url", "configuration-base-url"],
                    value=current_llm["base-url"],
                    help="Provider service URL. Default: https://api.openai.com/v1.",
                )
        st.text_input(
            label="Model",
            key="configuration-llm-model",
            on_change=configuration_callback,
            args=["llm", "model", "configuration-llm-model"],
            value=current_llm["model"],
            help=f"Model for this workflow. Default: {default_model}.",
        )
        st.number_input(
            label="Maximum number of tokens",
            key="configuration-llm-max-tokens",
            on_change=configuration_callback,
            args=["llm", "max-tokens", "configuration-llm-max-tokens"],
            value=current_llm["max-tokens"],
            help="""
                Maximum number of tokens the model can generate in a single response
                **Example: 1024**
                `Default: 4096`""",
        )
        st.number_input(
            label="Total number of model context",
            key="configuration-llm-context-window",
            on_change=configuration_callback,
            args=["llm", "context-window", "configuration-llm-context-window"],
            value=current_llm["context-window"],
            help="""
                Total number of model context in a single response (Input + Output)
                **Example: 200000**
                `Default: 200000`""",
        )
        direct_openai_gpt6 = (
            current_llm["api"] == "openai"
            and urlsplit(current_llm["base-url"]).hostname == "api.openai.com"
            and current_llm["model"].startswith(("gpt-6-", "gpt-6."))
        )
        if direct_openai_gpt6:
            st.caption("GPT-6 uses model-managed sampling; temperature and top-p are not sent.")
        else:
            st.selectbox(
                label="Temperature",
                key="configuration-llm-temperature",
                on_change=configuration_callback,
                args=["llm", "temperature", "configuration-llm-temperature"],
                options=(current_llm["temperature"], 0, 1),
                help="""
                    Sampling temperature to use for the LLM output (0 = deterministic, 1 = creative)
                    `Default: 0.05`""",
            )
            st.number_input(
                label="Top-p (Nucleus Sampling)",
                key="configuration-llm-top-p",
                on_change=configuration_callback,
                args=["llm", "top-p", "configuration-llm-top-p"],
                value=current_llm["top-p"],
                help="""
                    Nucleus sampling probability (1.0 = all tokens considered)
                    **Example: 0.8**
                    `Default: 0.95`""",
            )
