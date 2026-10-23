import shutil
from unittest import TestCase
from unittest.mock import patch

from osa_web.state import keys
from osa_web.ui import conversation


class ConversationTests(TestCase):
    def test_repository_url_requires_a_github_repository(self) -> None:
        self.assertTrue(conversation._is_github_repository_url("https://github.com/example/repo"))
        for value in (
            "https://github.com.example.org/example/repo",
            "https://github.com/example",
            "https://github.com/example/repo/tree/main",
            "http://github.com/example/repo",
            "https://github.com:abc/example/repo",
        ):
            with self.subTest(value=value):
                self.assertFalse(conversation._is_github_repository_url(value))

    def test_any_publishing_action_requires_confirmation(self) -> None:
        configuration = {"agentic": {"git": {"no-fork": False, "no-pull-request": False}}}
        with patch.object(conversation.st, "session_state", {keys.CONFIGURATION: configuration}):
            self.assertTrue(conversation._publishing_enabled())
            configuration["agentic"]["git"]["no-pull-request"] = True
            self.assertTrue(conversation._publishing_enabled())
            configuration["agentic"]["git"]["no-fork"] = True
            self.assertFalse(conversation._publishing_enabled())
            configuration["agentic"]["git"]["no-pull-request"] = False
            self.assertTrue(conversation._publishing_enabled())

    def test_publishing_run_is_staged_until_confirmed(self) -> None:
        state = {
            keys.CONFIGURATION: {"agentic": {"git": {"no-fork": False, "no-pull-request": False}}},
            keys.TMPDIR: "/tmp",
            keys.CHAT_ATTACHMENT: {
                "type": "URL",
                "data": "https://example.com/paper.pdf",
            },
        }
        with (
            patch.object(conversation.st, "session_state", state),
            patch.object(conversation, "is_guest_mode", return_value=False),
            patch.object(conversation, "_start_run") as start,
        ):
            conversation._stage_run("Improve the README", "https://github.com/example/repo")
        try:
            start.assert_not_called()
            self.assertEqual(state[keys.CHAT_PENDING]["request"], "Improve the README")
            self.assertEqual(
                state[keys.CHAT_PENDING]["attachment"], "https://example.com/paper.pdf"
            )
        finally:
            shutil.rmtree(state[keys.CHAT_PENDING]["output_dir"])
