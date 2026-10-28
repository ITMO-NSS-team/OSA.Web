from unittest import TestCase
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from osa_web.osa_tool.endpoint import check_endpoint


class EndpointTests(TestCase):
    def test_http_rejection_still_proves_endpoint_is_reachable(self) -> None:
        with patch("osa_web.osa_tool.endpoint.urlopen") as open_url:
            open_url.side_effect = HTTPError(
                "https://api.example/v1", 405, "Method Not Allowed", {}, None
            )
            check_endpoint({"api": "openai", "base-url": "https://api.example/v1"})
            self.assertEqual(open_url.call_args.args[0].get_method(), "HEAD")
            self.assertEqual(open_url.call_args.kwargs["timeout"], 3)

    def test_connection_error_names_endpoint_and_cause(self) -> None:
        with (
            patch("osa_web.osa_tool.endpoint.urlopen", side_effect=URLError("name not resolved")),
            self.assertRaisesRegex(RuntimeError, "api.example/v1: name not resolved"),
        ):
            check_endpoint({"api": "openai", "base-url": "https://api.example/v1"})

    def test_gateway_failure_reports_address_and_status(self) -> None:
        error = HTTPError("https://api.example/v1", 502, "Bad Gateway", {}, None)
        with (
            patch("osa_web.osa_tool.endpoint.urlopen", side_effect=error),
            self.assertRaisesRegex(RuntimeError, "api.example/v1 returned HTTP 502"),
        ):
            check_endpoint({"api": "openai", "base-url": "https://api.example/v1"})

    def test_invalid_url_fails_before_request(self) -> None:
        with (
            patch("osa_web.osa_tool.endpoint.urlopen") as open_url,
            self.assertRaisesRegex(RuntimeError, "Invalid LLM Base URL"),
        ):
            check_endpoint({"api": "openai", "base-url": "https://:wrong"})
            open_url.assert_not_called()

    def test_itmo_does_not_use_base_url(self) -> None:
        with patch("osa_web.osa_tool.endpoint.urlopen") as open_url:
            check_endpoint({"api": "itmo", "base-url": "https://not-used.example"})
            open_url.assert_not_called()
