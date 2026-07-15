from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from osa_web.settings import load_config


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
