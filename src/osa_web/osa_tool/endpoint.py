"""Fast connection check for the configured LLM endpoint."""

from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def check_endpoint(llm: dict) -> None:
    if llm.get("api") == "itmo":
        return  # The ITMO provider does not use the editable Base URL.

    url = llm.get("base-url", "").strip()
    try:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username:
            raise ValueError("expected an http:// or https:// URL with a host")
        _ = parsed.port  # Validate the port before making the request.
    except ValueError as exc:
        raise RuntimeError(f"Invalid LLM Base URL {url!r}: {exc}") from exc

    display_url = parsed._replace(query="", fragment="").geturl()
    try:
        with urlopen(Request(url, method="HEAD"), timeout=3):
            pass
    except HTTPError as exc:
        # API roots commonly reject HEAD or require authentication. Any HTTP
        # response proves the server is reachable. Gateway/server errors still
        # make a run unlikely to succeed, so report them before launching OSA.
        if exc.code >= 500 or exc.code == 407:
            raise RuntimeError(f"LLM Base URL {display_url} returned HTTP {exc.code}") from exc
        return
    except (URLError, TimeoutError, OSError) as exc:
        reason = getattr(exc, "reason", exc)
        raise RuntimeError(f"Cannot reach LLM Base URL {display_url}: {reason}") from exc
