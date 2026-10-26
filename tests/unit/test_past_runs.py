"""Validation and UI behavior for curated public run results."""

from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

import streamlit as st
from streamlit.testing.v1 import AppTest

from osa_web.past_runs import PastRun, load_past_runs, parse_past_runs

ENTRYPOINT = Path(__file__).resolve().parents[2] / "streamlit_app.py"

PIPELINE = {
    "id": "pipeline-one",
    "repository_url": "https://github.com/example/first-repo",
    "work_mode": "Automated pipeline",
    "completed_at": "2026-10-26",
    "outcome": "completed",
    "summary": "README updated.",
    "steps": ["Reviewed README", "Updated installation instructions"],
    "preset": "quality",
    "pull_request_url": "https://github.com/example/first-repo/pull/4",
}
AGENTIC = {
    "id": "agentic-one",
    "repository_url": "https://github.com/example/second-repo",
    "work_mode": "Agentic conversation",
    "completed_at": "2026-10-25",
    "outcome": "completed",
    "summary": "Tests added.",
    "steps": ["Planned coverage", "Added tests"],
    "request": "Add tests for the parser",
}


class PastRunDataTests(TestCase):
    def test_loads_packaged_catalogue(self) -> None:
        self.assertTrue(all(isinstance(run, PastRun) for run in load_past_runs()))

    def test_loads_valid_records_from_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "past_runs.json"
            path.write_text(json.dumps([PIPELINE, AGENTIC]), encoding="utf-8")
            runs = load_past_runs(path)
        self.assertEqual(
            [run.repository_name for run in runs], ["example/first-repo", "example/second-repo"]
        )
        self.assertEqual(runs[0].pull_request_url, PIPELINE["pull_request_url"])
        self.assertEqual(runs[1].request, AGENTIC["request"])

    def test_rejects_invalid_public_records(self) -> None:
        with self.assertRaisesRegex(TypeError, "JSON list"):
            parse_past_runs({"runs": []})
        invalid_changes = [
            {"id": ""},
            {"repository_url": "https://github.com.evil.test/example/repo"},
            {"completed_at": "2026-02-30"},
            {"outcome": "unknown"},
            {"steps": []},
            {"preset": "unknown"},
            {"pull_request_url": "https://github.com/elsewhere/repo/pull/1"},
            {"api_key": "secret"},
        ]
        for changes in invalid_changes:
            with self.subTest(changes=changes):
                record = copy.deepcopy(PIPELINE)
                record.update(changes)
                with self.assertRaisesRegex(ValueError, "Past run #1"):
                    parse_past_runs([record])

        with self.assertRaisesRegex(ValueError, "duplicate id"):
            parse_past_runs([PIPELINE, PIPELINE])
        with self.assertRaisesRegex(ValueError, "missing fields"):
            parse_past_runs([{key: value for key, value in AGENTIC.items() if key != "request"}])


class PastRunAppTests(TestCase):
    def _open_past_runs(self, app: AppTest) -> AppTest:
        app.session_state["osa-tabs"] = ":material/history: Past runs"
        return app.run()

    def test_guest_sees_empty_state(self) -> None:
        with patch("osa_web.ui.past_runs.load_past_runs", return_value=[]):
            app = AppTest.from_file(str(ENTRYPOINT), default_timeout=10).run()
            next(
                button for button in app.button if button.label == "Continue as guest"
            ).click().run()
            self._open_past_runs(app)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.tabs), 3)
        self.assertEqual(app.segmented_control(key="work_mode").value, "Automated pipeline")
        self.assertTrue(any("No past runs" in item.value for item in app.info))

    def test_guest_can_filter_numbered_results_and_open_details(self) -> None:
        records = parse_past_runs(
            [
                PIPELINE,
                AGENTIC,
                {
                    **PIPELINE,
                    "id": "pipeline-two",
                    "repository_url": "https://github.com/example/third-repo",
                    "pull_request_url": None,
                },
            ]
        )
        with patch("osa_web.ui.past_runs.load_past_runs", return_value=records):
            app = AppTest.from_file(str(ENTRYPOINT), default_timeout=10).run()
            next(
                button for button in app.button if button.label == "Continue as guest"
            ).click().run()
            self._open_past_runs(app)
            self.assertFalse(app.exception)
            self.assertEqual(
                [item.label for item in app.expander],
                ["1. example/first-repo", "2. example/third-repo"],
            )
            self.assertTrue(any("README updated." in item.value for item in app.markdown))
            self.assertTrue(any("View repository" in item.value for item in app.markdown))
            self.assertTrue(
                any(item.label == "View pull request" for item in app.get("link_button"))
            )

            app.segmented_control(key="work_mode").set_value("Agentic conversation").run()
            self.assertFalse(app.exception)
            self.assertEqual([item.label for item in app.expander], ["1. example/second-repo"])
            self.assertTrue(any("Add tests for the parser" in item.value for item in app.markdown))

    def test_authenticated_user_can_open_same_catalogue(self) -> None:
        records = parse_past_runs([AGENTIC])
        user = MagicMock(is_logged_in=True)
        user.get.return_value = "Test user"
        with (
            patch.object(st, "user", user),
            patch("osa_web.ui.past_runs.load_past_runs", return_value=records),
        ):
            app = AppTest.from_file(str(ENTRYPOINT), default_timeout=10).run()
            self._open_past_runs(app)
            app.segmented_control(key="work_mode").set_value("Agentic conversation").run()
        self.assertFalse(app.exception)
        self.assertEqual([item.label for item in app.expander], ["1. example/second-repo"])
