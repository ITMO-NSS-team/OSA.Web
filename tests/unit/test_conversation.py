import shutil
from datetime import UTC, datetime, timedelta
from unittest import TestCase
from unittest.mock import patch

from osa_web.state import keys
from osa_web.ui import conversation


class ConversationTests(TestCase):
    def test_elapsed_run_time(self) -> None:
        started = datetime(2026, 10, 26, 10, 0, tzinfo=UTC)

        self.assertEqual(
            conversation._elapsed_time(started, started + timedelta(seconds=65)), "01:05"
        )
        self.assertEqual(conversation._elapsed_time(None, started), "00:00")

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

    def test_process_exit_preserves_diagnostics_for_error_message(self) -> None:
        state = {
            keys.CHAT_TERMINAL: False,
            keys.CHAT_QUESTION: None,
            keys.CHAT_MESSAGES: [],
            keys.CHAT_SHOW_CONSOLE: False,
        }
        with patch.object(conversation.st, "session_state", state):
            conversation._record_event(
                {"type": "process_exit", "exit_code": 1, "diagnostics": ["invalid field"]}
            )
        self.assertEqual(state[keys.CHAT_MESSAGES][0]["event"]["diagnostics"], ["invalid field"])
        self.assertTrue(state[keys.CHAT_SHOW_CONSOLE])

    def test_protocol_error_keeps_stderr_on_process_exit(self) -> None:
        state = {
            keys.CHAT_TERMINAL: False,
            keys.CHAT_QUESTION: None,
            keys.CHAT_MESSAGES: [],
            keys.CHAT_SHOW_CONSOLE: False,
        }
        with patch.object(conversation.st, "session_state", state):
            conversation._record_event(
                {
                    "type": "error",
                    "message": "Error code: 401 - User not found.",
                    "recoverable": False,
                }
            )
            conversation._record_event(
                {"type": "process_exit", "exit_code": 1, "diagnostics": ["provider traceback"]}
            )
        self.assertEqual(len(state[keys.CHAT_MESSAGES]), 1)
        self.assertEqual(
            state[keys.CHAT_MESSAGES][0]["event"]["diagnostics"],
            ["provider traceback"],
        )
        self.assertTrue(state[keys.CHAT_SHOW_CONSOLE])

    def test_start_failure_remains_visible_after_rerun(self) -> None:
        state = {
            keys.CHAT_PENDING: {"repository": "https://github.com/example/repo"},
            keys.CHAT_MESSAGES: [],
        }
        with (
            patch.object(conversation.st, "session_state", state),
            patch.object(conversation.logger, "exception"),
        ):
            conversation._record_start_failure(RuntimeError("Cannot reach LLM Base URL"))
        self.assertIsNone(state[keys.CHAT_PENDING])
        self.assertIn("Cannot reach LLM Base URL", state[keys.CHAT_MESSAGES][0]["event"]["message"])
