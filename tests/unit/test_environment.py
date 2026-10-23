import os
from unittest import TestCase
from unittest.mock import patch

from osa_web.osa_tool.environment import build_osa_environment


class EnvironmentTests(TestCase):
    def test_guest_receives_only_explicit_credentials(self) -> None:
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "server-secret",
                "OPENAI_KEY": "stale-secret",
                "GIT_TOKEN": "server-git",
                "PATH": "/bin",
            },
            clear=True,
        ):
            guest = build_osa_environment(guest=True, api_key="guest-key", git_token="server-git")
            authenticated = build_osa_environment(guest=False, api_key=None, git_token="server-git")
        self.assertEqual(guest["OPENAI_API_KEY"], "guest-key")
        self.assertEqual(guest["OPENAI_KEY"], "guest-key")
        self.assertNotIn("GIT_TOKEN", guest)
        self.assertEqual(authenticated["OPENAI_API_KEY"], "server-secret")
        self.assertEqual(authenticated["OPENAI_KEY"], "server-secret")
        self.assertEqual(authenticated["GIT_TOKEN"], "server-git")
