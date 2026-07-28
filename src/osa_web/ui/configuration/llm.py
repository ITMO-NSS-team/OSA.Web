from __future__ import annotations

import streamlit as st

from osa_web.auth.state import is_guest_mode
from osa_web.ui.configuration.schema import configuration_callback, current_section


@st.fragment
def render_llm_settings_block() -> None:
    with st.container(border=True):
        st.markdown(
            '<h5 style="text-align: center;">LLM Settings</h5>',
            unsafe_allow_html=True,
        )
        current_llm = current_section("llm")
        if is_guest_mode():
            llm_api_options = ("openai", "llama", "ollama")
            st.selectbox(
                label="API",
                key="configuration-llm-api",
                on_change=configuration_callback,
                args=["llm", "api", "configuration-llm-api"],
                options=llm_api_options,
                help="""
                    LLM API service provider
                    `Default: openai`
                    """,
            )
            st.text_input(
                label="API Key :red[*] :red-background[**WARNING**: PLEASE USE THROWAWAY KEYS]",
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
                value=current_llm["base-url"],
                help="""
                    URL of the provider compatible with OpenAI API
                    `Default: https://api.openai.com/v1`""",
            )
        else:
            llm_api_options = ("itmo", "openai", "llama", "ollama")
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
                    `Default: itmo`
                    """,
            )
            if current_llm["api"] != "itmo":
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
                    value=current_llm["base-url"],
                    help="""
                        URL of the provider compatible with OpenAI API
                        `Default: https://api.openai.com/v1`""",
                )
        st.text_input(
            label="Model",
            key="configuration-llm-model",
            on_change=configuration_callback,
            args=["llm", "model", "configuration-llm-model"],
            value=current_llm["model"],
            help="""
                Specific LLM model to use
                `Default: gpt-4o-mini`
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
                `Default: 16385`""",
        )
        st.selectbox(
            label="Temperature",
            key="configuration-llm-temperature",
            on_change=configuration_callback,
            args=["llm", "temperature", "configuration-llm-temperature"],
            options=(current_llm["temperature"], 0, 1),
            help="""
                Sampling temperature to use for the LLM output (0 = deterministic, 1 = creative)
                `Default: None`""",
        )
        st.number_input(
            label="Top-p (Nucleus Sampling)",
            key="configuration-llm-top-p",
            on_change=configuration_callback,
            args=["llm", "top-p", "configuration-llm-top-p"],
            value=current_llm["top-p"],
            help="""
                Nucleus sampling probability (1.0 = all tokens considered)
                *Example: 0.8**
                `Default: None`""",
        )
