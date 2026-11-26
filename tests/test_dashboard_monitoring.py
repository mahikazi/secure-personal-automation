import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from dashboard.app import SecureFlow


class TestDashboardMonitoring(unittest.TestCase):

    def setUp(self):
        self.app = Mock()

        self.logs = [
            "2026-11-26T10:00:00 | SUCCESS | example.txt",
            "2026-11-26T10:01:00 | BLOCKED | example.exe",
            "2026-11-26T10:02:00 | CANCELLED | archive.txt"
        ]

        self.app.logs.return_value = self.logs
        self.app.search.get.return_value = ""
        self.app.filter.get.return_value = "ALL"

    @patch("dashboard.app.Path.exists", return_value=False)
    def test_missing_audit_log(self, exists):
        result = SecureFlow.logs(self.app)

        self.assertEqual(result, [])

    def test_activity_search(self):
        self.app.search.get.return_value = "EXAMPLE.TXT"

        SecureFlow.refresh_logs(self.app)

        self.app.write.assert_called_once_with(
            self.app.log_box,
            self.logs[0]
        )

    def test_activity_status_filter(self):
        self.app.filter.get.return_value = "BLOCKED"

        SecureFlow.refresh_logs(self.app)

        self.app.write.assert_called_once_with(
            self.app.log_box,
            self.logs[1]
        )

    @patch("dashboard.app.save_history")
    @patch("dashboard.app.load_history", return_value={})
    @patch("dashboard.app.current_time")
    def test_schedule_history_updated(self, now, load, save):
        timestamp = datetime(
            2026, 11, 26, 10, 0,
            tzinfo=timezone.utc
        )

        now.return_value = timestamp

        schedule = {"name": "daily_organizer"}

        SecureFlow.record_schedule(self.app, schedule)

        save.assert_called_once_with({
            "daily_organizer": timestamp
        })

    @patch("dashboard.app.load_schedules")
    @patch("dashboard.app.load_history")
    @patch("dashboard.app.get_due_schedules")
    def test_due_schedule_preview(self, due, history, schedules):
        schedule = {
            "name": "daily_organizer",
            "workflow": "organize",
            "interval_minutes": 1440,
            "enabled": True
        }

        due.return_value = [schedule]

        self.app.schedule_choice.get.return_value = (
            "daily_organizer"
        )

        SecureFlow.schedule_preview(self.app)

        self.app.preview.assert_called_once_with(
            "organize", 30, schedule
        )

    @patch("dashboard.app.load_schedules")
    @patch("dashboard.app.load_history")
    @patch("dashboard.app.get_due_schedules", return_value=[])
    @patch("dashboard.app.messagebox.showerror")
    def test_schedule_no_longer_due(
        self, error, due, history, schedules
    ):
        self.app.schedule_choice.get.return_value = (
            "daily_organizer"
        )

        SecureFlow.schedule_preview(self.app)

        self.app.preview.assert_not_called()

        error.assert_called_once_with(
            "Schedule preview failed",
            "This schedule is no longer due. Refresh schedules.",
            parent=self.app
        )


if __name__ == "__main__":
    unittest.main()