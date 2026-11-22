import unittest
from unittest.mock import patch

from scheduler.scheduled_runner import (
    run_scheduled_workflow,
    run_due_schedules
)


class TestScheduledRunner(unittest.TestCase):

    def setUp(self):
        self.schedule = {
            "name": "daily_organizer",
            "workflow": "organize",
            "interval_minutes": 60,
            "enabled": True
        }

    @patch("scheduler.scheduled_runner.execute_approved_actions")
    @patch("scheduler.scheduled_runner.run_workflow")
    def test_organizer_uses_approval(
        self, mock_workflow, mock_execute
    ):
        actions = [
            {
                "source": "test_files/a.txt",
                "destination": "test_files/txt/a.txt"
            }
        ]

        mock_workflow.return_value = actions
        mock_execute.return_value = 1

        result = run_scheduled_workflow(
            self.schedule,
            "test_files"
        )

        mock_execute.assert_called_once_with(
            actions,
            "test_files"
        )
        self.assertEqual(result, 1)

    @patch("scheduler.scheduled_runner.execute_approved_actions")
    @patch("scheduler.scheduled_runner.run_workflow")
    def test_duplicates_do_not_use_executor(
        self, mock_workflow, mock_execute
    ):
        schedule = self.schedule.copy()
        schedule["workflow"] = "duplicates"

        mock_workflow.return_value = [
            {
                "original": "a.txt",
                "duplicate": "b.txt"
            }
        ]

        result = run_scheduled_workflow(
            schedule,
            "test_files"
        )

        self.assertEqual(result, 0)
        mock_execute.assert_not_called()

    @patch("scheduler.scheduled_runner.save_history")
    @patch("scheduler.scheduled_runner.load_history")
    @patch("scheduler.scheduled_runner.load_schedules")
    @patch("scheduler.scheduled_runner.run_scheduled_workflow")
    def test_due_schedule_runs(
        self,
        mock_run,
        mock_load_schedules,
        mock_load_history,
        mock_save_history
    ):
        mock_load_schedules.return_value = [self.schedule]
        mock_load_history.return_value = {}

        result = run_due_schedules()

        self.assertEqual(result, 1)
        mock_run.assert_called_once()
        mock_save_history.assert_called_once()

    @patch("scheduler.scheduled_runner.save_history")
    @patch("scheduler.scheduled_runner.load_history")
    @patch("scheduler.scheduled_runner.load_schedules")
    @patch("scheduler.scheduled_runner.run_scheduled_workflow")
    def test_no_due_schedules(
        self,
        mock_run,
        mock_load_schedules,
        mock_load_history,
        mock_save_history
    ):
        schedule = self.schedule.copy()
        schedule["enabled"] = False

        mock_load_schedules.return_value = [schedule]
        mock_load_history.return_value = {}

        result = run_due_schedules()

        self.assertEqual(result, 0)
        mock_run.assert_not_called()
        mock_save_history.assert_not_called()


if __name__ == "__main__":
    unittest.main()