import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from config.config_loader import (
    load_config,
    save_config,
    validate_config
)


class TestConfigLoader(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.root = Path(self.temp.name).resolve()
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()

        self.default = self.root / "settings.json"
        self.local = self.root / "settings.local.json"

        self.settings = {
            "allowed_folder": str(self.workspace),
            "allowed_extensions": [".txt", ".pdf"],
            "max_file_size_mb": 20
        }

        self.default.write_text(
            json.dumps(self.settings),
            encoding="utf-8"
        )

        config_patch = patch.multiple(
            "config.config_loader",
            CONFIG_DIR=self.root,
            DEFAULT_CONFIG=self.default,
            LOCAL_CONFIG=self.local
        )

        config_patch.start()
        self.addCleanup(config_patch.stop)

    def test_load_default_configuration(self):
        self.assertEqual(load_config(), self.settings)

    def test_local_configuration_takes_priority(self):
        settings = dict(self.settings)
        settings["max_file_size_mb"] = 50

        self.local.write_text(
            json.dumps(settings),
            encoding="utf-8"
        )

        self.assertEqual(load_config(), settings)

    def test_save_creates_local_configuration(self):
        save_config(self.settings)

        self.assertTrue(self.local.exists())
        self.assertEqual(load_config(), self.settings)

    def test_default_configuration_preserved(self):
        original = self.default.read_bytes()

        settings = dict(self.settings)
        settings["max_file_size_mb"] = 50

        save_config(settings)

        self.assertEqual(self.default.read_bytes(), original)
        self.assertEqual(load_config()["max_file_size_mb"], 50)

    def test_missing_configuration(self):
        self.default.unlink()

        with self.assertRaises(ValueError):
            load_config()

    def test_invalid_json(self):
        self.local.write_text(
            "invalid json",
            encoding="utf-8"
        )

        with self.assertRaises(ValueError):
            load_config()

    def test_invalid_workspace_values(self):
        for value in ["", " ", None, 123, "bad\x00path"]:
            with self.subTest(value=value):
                settings = dict(self.settings)
                settings["allowed_folder"] = value

                with self.assertRaises(ValueError):
                    validate_config(settings)

    def test_invalid_extensions(self):
        for extensions in [
            [],
            "txt",
            ["txt"],
            ["."],
            [".txt/invalid"],
            [".txt\\invalid"],
            [".txt\x00"],
            [123]
        ]:
            with self.subTest(extensions=extensions):
                settings = dict(self.settings)
                settings["allowed_extensions"] = extensions

                with self.assertRaises(ValueError):
                    validate_config(settings)

    def test_invalid_size_limits(self):
        for size in [
            0,
            -1,
            True,
            None,
            "20",
            float("inf"),
            float("-inf"),
            float("nan")
        ]:
            with self.subTest(size=size):
                settings = dict(self.settings)
                settings["max_file_size_mb"] = size

                with self.assertRaises(ValueError):
                    validate_config(settings)

    def test_extension_normalization(self):
        settings = dict(self.settings)
        settings["allowed_extensions"] = [
            ".TXT",
            ".txt",
            ".PDF"
        ]

        validated = validate_config(settings)

        self.assertEqual(
            validated["allowed_extensions"],
            [".txt", ".pdf"]
        )

    def test_save_rejects_missing_workspace(self):
        settings = dict(self.settings)
        settings["allowed_folder"] = str(
            self.root / "missing"
        )

        with self.assertRaises(ValueError):
            save_config(settings)

        self.assertFalse(self.local.exists())

    def test_save_rejects_file_as_workspace(self):
        file = self.root / "notes.txt"
        file.write_text("Content")

        settings = dict(self.settings)
        settings["allowed_folder"] = str(file)

        with self.assertRaises(ValueError):
            save_config(settings)

        self.assertFalse(self.local.exists())

    def test_failed_save_preserves_previous_configuration(self):
        save_config(self.settings)
        original = self.local.read_bytes()

        settings = dict(self.settings)
        settings["max_file_size_mb"] = 50

        with patch(
            "config.config_loader.os.replace",
            side_effect=OSError("Simulated failure")
        ):
            with self.assertRaises(OSError):
                save_config(settings)

        self.assertEqual(self.local.read_bytes(), original)

    def test_temporary_file_cleanup(self):
        save_config(self.settings)

        self.assertEqual(
            list(self.root.glob(".settings_*.tmp")),
            []
        )

    def test_failed_save_cleans_temporary_file(self):
        with patch(
            "config.config_loader.os.replace",
            side_effect=OSError("Simulated failure")
        ):
            with self.assertRaises(OSError):
                save_config(self.settings)

        self.assertEqual(
            list(self.root.glob(".settings_*.tmp")),
            []
        )


if __name__ == "__main__":
    unittest.main()