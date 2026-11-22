import json
import tempfile
import unittest
from pathlib import Path

from scheduler.schedule_config import load_schedules


class TestScheduleConfig(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.config_path = Path(self.temp_dir.name) / "schedules.json"

        self.valid_schedule = {
            "name": "daily_organizer",
            "workflow": "organize",
            "interval_minutes": 1440,
            "enabled": True
        }

    def write_config(self, schedules):
        self.config_path.write_text(
            json.dumps({"schedules": schedules}),
            encoding="utf-8"
        )

    def test_loads_valid_schedule(self):
        self.write_config([self.valid_schedule])

        schedules = load_schedules(self.config_path)

        self.assertEqual(len(schedules), 1)
        self.assertEqual(schedules[0]["workflow"], "organize")

    def test_rejects_unknown_workflow(self):
        schedule = self.valid_schedule.copy()
        schedule["workflow"] = "delete_everything"

        self.write_config([schedule])

        with self.assertRaises(ValueError):
            load_schedules(self.config_path)

    def test_rejects_invalid_interval(self):
        schedule = self.valid_schedule.copy()
        schedule["interval_minutes"] = 0

        self.write_config([schedule])

        with self.assertRaises(ValueError):
            load_schedules(self.config_path)

    def test_rejects_duplicate_names(self):
        self.write_config([
            self.valid_schedule,
            self.valid_schedule.copy()
        ])

        with self.assertRaises(ValueError):
            load_schedules(self.config_path)

    def test_archive_requires_days_old(self):
        schedule = self.valid_schedule.copy()
        schedule["workflow"] = "archive"

        self.write_config([schedule])

        with self.assertRaises(ValueError):
            load_schedules(self.config_path)


if __name__ == "__main__":
    unittest.main()