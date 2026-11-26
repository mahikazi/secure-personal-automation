import json
import unittest
import tempfile

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, mock_open

from config.config_loader import load_config
from security.audit_logger import log_action
from scheduler.schedule_history import load_history, save_history


class TestRuntimeIntegrity(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.root = Path(self.temp.name)
        self.history_path = self.root / "schedule_history.json"

        self.settings = {
            "allowed_folder": "test_files",
            "allowed_extensions": [".txt"],
            "max_file_size_mb": 20
        }

        self.timestamp = datetime(
            2026, 11, 26, 12, 0,
            tzinfo=timezone.utc
        )

    def test_non_finite_file_size_rejected(self):
        for value in (
            float("nan"),
            float("inf"),
            float("-inf")
        ):
            with self.subTest(value=value):
                self.settings["max_file_size_mb"] = value

                content = json.dumps(self.settings)

                with patch(
                    "pathlib.Path.open",
                    mock_open(read_data=content)
                ):
                    with self.assertRaises(ValueError):
                        load_config()

    def test_audit_log_injection_prevented(self):
        action = {
            "source": "example.txt\nFAKE | SUCCESS",
            "destination": "txt/example.txt"
        }

        mocked_file = mock_open()

        with patch("pathlib.Path.open", mocked_file):
            log_action(action, "BLOCKED")

        content = mocked_file().write.call_args.args[0]

        self.assertEqual(content.count("\n"), 1)
        self.assertEqual(content.count("|"), 2)
        self.assertIn("\\n", content)
        self.assertIn("\\x7c", content)

    def test_history_round_trip(self):
        history = {
            "daily_organizer": self.timestamp
        }

        save_history(history, self.history_path)

        loaded = load_history(self.history_path)

        self.assertEqual(loaded, history)

    def test_naive_history_timestamp_rejected(self):
        history = {
            "daily_organizer": datetime(2026, 11, 26)
        }

        with self.assertRaises(ValueError):
            save_history(history, self.history_path)

        self.assertFalse(self.history_path.exists())

    def test_failed_history_write_preserves_previous_data(self):
        original = {
            "daily_organizer": self.timestamp
        }

        save_history(original, self.history_path)

        updated = {
            "weekly_archiver": self.timestamp
        }

        with patch(
            "scheduler.schedule_history.os.replace",
            side_effect=OSError("Replacement failed")
        ):
            with self.assertRaises(OSError):
                save_history(updated, self.history_path)

        self.assertEqual(
            load_history(self.history_path),
            original
        )

        temporary_files = list(
            self.root.glob(".schedule_history_*.tmp")
        )

        self.assertEqual(temporary_files, [])


if __name__ == "__main__":
    unittest.main()