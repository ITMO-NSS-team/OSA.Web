from datetime import UTC, datetime, timedelta, timezone
from unittest import TestCase

from osa_web.ui.console_output import console_filename


class ConsoleOutputTests(TestCase):
    def test_filename_uses_repository_and_utc_run_start(self) -> None:
        started = datetime(2026, 10, 26, 5, 55, tzinfo=timezone(timedelta(hours=3)))

        self.assertEqual(
            console_filename("https://github.com/aimclub/OSA", started),
            "aimclub-osa-20261026-025500Z.txt",
        )

    def test_missing_repository_uses_safe_name(self) -> None:
        started = datetime(2026, 10, 26, tzinfo=UTC)

        self.assertEqual(console_filename("", started), "osa-run-20261026-000000Z.txt")
