import os
import tomllib
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from osa_web import __version__, settings
from osa_web.settings import CONFIG_PATH, get_runtime_path, load_config


class SettingsTests(TestCase):
    def test_version_comes_from_pyproject(self) -> None:
        with (settings.PROJECT_ROOT / "pyproject.toml").open("rb") as file:
            self.assertEqual(__version__, tomllib.load(file)["project"]["version"])

    def test_explicit_config_overrides_defaults(self) -> None:
        with TemporaryDirectory() as tmpdir:
            override_path = Path(tmpdir) / "override.toml"
            override_path.write_text(
                """
                [fast.llm]
                model = "override-model"
                """,
                encoding="utf-8",
            )

            config = load_config(override_path)

        self.assertEqual(config["fast"]["llm"]["model"], "override-model")
        self.assertIn("quality", config)
        self.assertIn("agentic", config)
        self.assertEqual(config["agentic"]["git"]["no-pull-request"], False)

    def test_config_exists_for_docker_builds(self) -> None:
        self.assertTrue(CONFIG_PATH.exists())

    def test_runtime_paths_use_environment_with_relative_defaults(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_runtime_path("tmp"), settings.PROJECT_ROOT / "runtime/tmp")
            self.assertEqual(
                get_runtime_path("log"), settings.PROJECT_ROOT / "runtime/logs/osa_web.logs"
            )
        with patch.dict(
            os.environ,
            {"OSA_WEB_TMP_DIR": "/var/essdata/tmp", "OSA_WEB_LOG_PATH": "server/logs/web.log"},
        ):
            self.assertEqual(get_runtime_path("tmp"), Path("/var/essdata/tmp"))
            self.assertEqual(get_runtime_path("log"), settings.PROJECT_ROOT / "server/logs/web.log")

    def test_legacy_openrouter_provider_is_migrated_without_changing_real_itmo(self) -> None:
        with TemporaryDirectory() as tmpdir:
            override_path = Path(tmpdir) / "override.toml"
            override_path.write_text(
                '[fast.llm]\napi = "itmo"\nbase-url = "https://openrouter.ai/api/v1"\n'
                '[agentic.llm]\napi = "itmo"\nbase-url = "https://itmo.example/api/v1"\n',
                encoding="utf-8",
            )
            config = load_config(override_path)
        self.assertEqual(config["fast"]["llm"]["api"], "openai")
        self.assertEqual(config["agentic"]["llm"]["api"], "itmo")

    def test_missing_config_raises_clear_error(self) -> None:
        with TemporaryDirectory() as tmpdir:
            missing_path = Path(tmpdir) / "missing.toml"
            with (
                patch.object(settings, "CONFIG_PATH", missing_path),
                patch.dict(os.environ, {}, clear=True),
                self.assertRaisesRegex(RuntimeError, "config.toml"),
            ):
                load_config()
