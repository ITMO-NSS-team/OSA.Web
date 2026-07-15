from unittest import TestCase

from osa_web.osa_tool.command import build_osa_command
from osa_web.osa_tool.models import OsaRunRequest


class CommandBuilderTests(TestCase):
    def test_builds_osa_command_from_selected_mode(self) -> None:
        config = {
            "fast": {
                "git": {"branch": "main", "no-fork": False, "no-pull-request": True},
                "general": {"readme": True, "translate-readme": "", "report": False},
                "llm": {"api": "itmo", "model": "model-a", "temperature": 0.1},
                "workflows": {
                    "generate-workflows": True,
                    "python-versions": ["3.10", "3.11"],
                    "include-tests": True,
                },
            }
        }

        cmd = build_osa_command(
            OsaRunRequest(
                repo_url="https://github.com/example/repo",
                mode="fast",
                output_dir="/tmp/osa",
                author="Tester",
                configuration=config,
                attachment="/tmp/file.pdf",
            )
        )

        self.assertEqual(
            cmd[:7],
            [
                "osa-tool",
                "-r",
                "https://github.com/example/repo",
                "-m",
                "advanced",
                "-o",
                "/tmp/osa",
            ],
        )
        self.assertIn("--attachment", cmd)
        self.assertIn("--no-pull-request", cmd)
        self.assertIn("--readme", cmd)
        self.assertIn("--api", cmd)
        self.assertIn("openai", cmd)
        self.assertIn("3.10, 3.11", cmd)
