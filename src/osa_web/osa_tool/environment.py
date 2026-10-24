"""Environment passed to OSA subprocesses."""

from __future__ import annotations

import os

GUEST_ENV_KEYS = {
    "PATH",
    "HOME",
    "USER",
    "LANG",
    "TMPDIR",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "NO_PROXY",
    "http_proxy",
    "https_proxy",
    "no_proxy",
    "SSL_CERT_FILE",
    "SSL_CERT_DIR",
    "REQUESTS_CA_BUNDLE",
    "CURL_CA_BUNDLE",
    # Windows needs these: without SYSTEMROOT, Winsock cannot initialise and any
    # child that imports asyncio dies with WinError 10106 before logging starts;
    # USERPROFILE stands in for HOME, which Windows does not set.
    "SYSTEMROOT",
    "USERPROFILE",
    "TEMP",
    "TMP",
}


def build_osa_environment(
    *, guest: bool, api_key: str | None, git_token: str | None
) -> dict[str, str]:
    if guest:
        env = {
            key: value
            for key, value in os.environ.items()
            if key in GUEST_ENV_KEYS or key.startswith("LC_")
        }
    else:
        env = os.environ.copy()
    env.update({"COLUMNS": "200", "TERM": "xterm-256color", "PYTHONUNBUFFERED": "1"})
    if api_key:
        env["OPENAI_API_KEY"] = api_key
        env["OPENAI_KEY"] = api_key
    elif not guest and env.get("OPENAI_API_KEY"):
        # ProtoLLM reads OPENAI_KEY; the Web app's existing .env uses OPENAI_API_KEY.
        env["OPENAI_KEY"] = env["OPENAI_API_KEY"]
    if git_token and not guest:
        env["GIT_TOKEN"] = git_token
    return env
