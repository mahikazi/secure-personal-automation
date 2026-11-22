import unittest
from datetime import datetime, timedelta, timezone

from scheduler.schedule_manager import (
    is_schedule_due,
    get_due_schedules
)


class TestScheduleManager(unittest.TestCase):

    def setUp(self):
        self.now = datetime(
            2026, 11, 21, 12, 0,
            tzinfo=timezone.utc
        )

        self.schedule = {
            "name": "daily_organizer",
            "workflow": "organize",
            "interval_minutes": 60,
            "enabled": True
        }

    def test_new_schedule_is_due(self):
        self.assertTrue(
            is_schedule_due(self.schedule, None, self.now)
        )

    def test_disabled_schedule_is_not_due(self):
        schedule = self.schedule.copy()
        schedule["enabled"] = False

        self.assertFalse(
            is_schedule_due(schedule, None, self.now)
        )

    def test_schedule_is_due_after_interval(self):
        last_run = self.now - timedelta(minutes=90)

        self.assertTrue(
            is_schedule_due(self.schedule, last_run, self.now)
        )

    def test_schedule_is_not_due_before_interval(self):
        last_run = self.now - timedelta(minutes=30)

        self.assertFalse(
            is_schedule_due(self.schedule, last_run, self.now)
        )

    def test_get_due_schedules_filters_results(self):
        second_schedule = self.schedule.copy()
        second_schedule["name"] = "second"
        second_schedule["enabled"] = False

        due = get_due_schedules(
            [self.schedule, second_schedule],
            {},
            self.now
        )

        self.assertEqual(len(due), 1)
        self.assertEqual(
            due[0]["name"],
            "daily_organizer"
        )


if __name__ == "__main__":
    unittest.main()