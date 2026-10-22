from unittest import TestCase

from osa_web.osa_tool.command import build_chat_command, build_osa_command
from osa_web.osa_tool.models import OsaChatRequest, OsaRunRequest


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
        self.assertIn("itmo", cmd)
        self.assertEqual(
            cmd[cmd.index("--python-versions") + 1 : cmd.index("--python-versions") + 3],
            ["3.10", "3.11"],
        )

    def test_new_list_options_and_empty_notebook_scan(self) -> None:
        config = {
            "quality": {
                "git": {"no-pull-request": True},
                "general": {
                    "target-files": 'src/main.py "docs/my file.md"',
                    "notebook-report": True,
                    "notebook-report-paths": "",
                    "scorecard": True,
                    "incremental": True,
                },
                "llm": {"api": "ollama"},
                "workflows": {"generate-workflows": True, "include-ruff": True, "use-uv": True},
            }
        }
        cmd = build_osa_command(
            OsaRunRequest(
                "https://github.com/example/repo", "quality", "/tmp/output", "Tester", config
            )
        )
        self.assertEqual(
            cmd[cmd.index("--target-files") + 1 : cmd.index("--target-files") + 3],
            ["src/main.py", "docs/my file.md"],
        )
        self.assertIn("--notebook-report", cmd)
        self.assertNotIn("--notebook-report-paths", cmd)
        self.assertIn("--scorecard", cmd)
        self.assertIn("--incremental", cmd)
        self.assertIn("--include-ruff", cmd)
        self.assertIn("--use-uv", cmd)

    def test_chat_command_uses_agentic_settings_only(self) -> None:
        cmd = build_chat_command(
            OsaChatRequest(
                output_dir="/tmp/session",
                log_dir="/tmp/logs",
                author="Tester",
                configuration={
                    "agentic": {
                        "git": {"no-fork": True},
                        "llm": {"api": "itmo", "model": "model-a"},
                    },
                    "quality": {"general": {"readme": True}},
                },
            )
        )
        self.assertEqual(cmd[1:4], ["-m", "osa_tool.run_chat", "--web-chat"])
        self.assertIn("--log-dir", cmd)
        self.assertIn("--no-fork", cmd)
        self.assertIn("itmo", cmd)
        self.assertNotIn("--readme", cmd)
