import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from osa_web import settings
from osa_web.settings import DEFAULT_CONFIG_PATH, load_config


class SettingsTests(TestCase):
    def test_explicit_config_overrides_defaults(self) -> None:
        with TemporaryDirectory() as tmpdir:
            override_path = Path(tmpdir) / "override.toml"
            override_path.write_text(
                """
                [paths]
                tmp = "custom/tmp"

                [fast.llm]
                model = "override-model"
                """,
                encoding="utf-8",
            )

            config = load_config(override_path)

        self.assertEqual(config["paths"]["tmp"], "custom/tmp")
        self.assertEqual(config["fast"]["llm"]["model"], "override-model")
        self.assertIn("quality", config)

    def test_default_config_exists_for_docker_builds(self) -> None:
        self.assertTrue(DEFAULT_CONFIG_PATH.exists())

    def test_missing_config_raises_clear_error(self) -> None:
        with TemporaryDirectory() as tmpdir:
            missing_path = Path(tmpdir) / "missing.toml"
            with (
                patch.object(settings, "DEFAULT_CONFIG_PATH", missing_path),
                patch.object(settings, "LEGACY_CONFIG_PATH", missing_path),
                patch.object(settings, "LOCAL_CONFIG_PATH", missing_path),
                patch.dict(os.environ, {}, clear=True),
            ):
                with self.assertRaisesRegex(RuntimeError, "config/default.toml"):
                    load_config()
