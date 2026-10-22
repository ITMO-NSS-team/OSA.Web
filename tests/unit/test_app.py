import tomllib
from pathlib import Path
from unittest import TestCase

from streamlit.testing.v1 import AppTest

from osa_web import __version__

ENTRYPOINT = Path(__file__).resolve().parents[2] / "streamlit_app.py"
PROJECT_VERSION = tomllib.loads((ENTRYPOINT.parent / "pyproject.toml").read_text(encoding="utf-8"))[
    "project"
]["version"]


class AppTests(TestCase):
    def test_guest_switches_home_workflows_and_their_settings(self) -> None:
        app = AppTest.from_file(str(ENTRYPOINT), default_timeout=10).run()
        next(button for button in app.button if button.label == "Continue as guest").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.tabs), 2)
        self.assertEqual(__version__, PROJECT_VERSION)
        self.assertTrue(
            any(f"Web Version: {PROJECT_VERSION}" in item.value for item in app.markdown)
        )
        self.assertEqual(app.segmented_control(key="work_mode").value, "Automated pipeline")
        self.assertIsNotNone(app.pills(key="attachment_selection_pills"))

        app.session_state["osa-tabs"] = ":material/settings: Configuration"
        app.run()
        self.assertEqual(app.segmented_control(key="configuration-preset").value, "quality")
        self.assertEqual(app.text_input(key="configuration-llm-model").value, "gpt-6-sol")
        app.segmented_control(key="configuration-preset").set_value("fast").run()
        self.assertEqual(app.session_state["mode_select"], "fast")
        self.assertEqual(app.text_input(key="configuration-llm-model").value, "gpt-6-luna")
        app.session_state["osa-tabs"] = ":material/home: Home"
        app.run()
        self.assertEqual(app.selectbox(key="mode_select").value, "fast")
        app.session_state["osa-tabs"] = ":material/settings: Configuration"
        app.run()
        self.assertEqual(app.segmented_control(key="configuration-preset").value, "fast")
        app.segmented_control(key="configuration-preset").set_value("quality").run()
        self.assertEqual(app.text_input(key="configuration-llm-model").value, "gpt-6-sol")
        app.text_input(key="configuration-api-key").set_value("current-test-key").run()

        app.session_state["osa-tabs"] = ":material/home: Home"
        self.assertFalse(app.exception)
        app.run()
        app.segmented_control(key="work_mode").set_value("Agentic conversation").run()
        self.assertEqual(len(app.chat_input), 1)
        self.assertFalse(any(button.label == "New conversation" for button in app.button))
        self.assertIsNotNone(app.button(key="chat_attachment-choose-url"))
        self.assertIsNotNone(app.button(key="chat_attachment-choose-file"))
        app.button(key="chat_attachment-choose-url").click().run()
        app.text_input(key="chat_attachment-url").set_value("https://example.com/paper.pdf").run()
        app.button(key="chat_attachment-submit").click().run()
        self.assertEqual(app.session_state["chat_attachment"]["type"], "URL")

        app.session_state["osa-tabs"] = ":material/settings: Configuration"
        app.run()
        self.assertEqual(app.text_input(key="configuration-llm-model").value, "gpt-6-luna")
        app.text_input(key="configuration-agentic-api-key").set_value("agentic-test-key").run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.checkbox), 2)
        self.assertEqual(app.session_state["configuration-api-key"], "current-test-key")
        self.assertEqual(app.session_state["configuration-agentic-api-key"], "agentic-test-key")

        app.session_state["osa-tabs"] = ":material/home: Home"
        app.session_state["chat_messages"] = [{"role": "user", "content": "Test request"}]
        app.run()
        app.button(key="chat-new-conversation").click().run()
        self.assertEqual(app.session_state["chat_messages"], [])
        self.assertFalse(any(button.label == "New conversation" for button in app.button))
