import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from main import main
from scheduler.scheduled_runner import run_due_schedules


class TestCLIIntegration(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workspace = self.temp_dir.name

        self.settings = {
            "allowed_folder": self.workspace,
            "allowed_extensions": [".txt"],
            "max_file_size_mb": 20
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_organizer_uses_configured_workspace(self):
        with patch("main.load_config", return_value=self.settings), \
             patch("builtins.input", return_value="1"), \
             patch("main.run_workflow", return_value=[]) as workflow, \
             patch("main.execute_approved_actions") as executor:

            main()

            workflow.assert_called_once_with(
                "organize", self.workspace
            )

            executor.assert_called_once_with(
                [], self.workspace
            )

    def test_missing_workspace_is_rejected(self):
        self.settings["allowed_folder"] = str(
            Path(self.workspace) / "missing"
        )

        with patch("main.load_config", return_value=self.settings), \
             patch("main.run_workflow") as workflow, \
             patch("builtins.print") as output:

            main()

            workflow.assert_not_called()

            output.assert_any_call(
                f"ERROR: Workspace does not exist: "
                f"{self.settings['allowed_folder']}"
            )

    def test_invalid_archive_age_is_rejected(self):
        with patch("main.load_config", return_value=self.settings), \
             patch("builtins.input", side_effect=["2", "-5"]), \
             patch("main.run_workflow") as workflow, \
             patch("builtins.print") as output:

            main()

            workflow.assert_not_called()

            output.assert_any_call(
                "Please enter a positive whole number."
            )

    def test_cli_passes_configured_workspace_to_scheduler(self):
        with patch("main.load_config", return_value=self.settings), \
             patch("builtins.input", return_value="4"), \
             patch("main.run_due_schedules") as scheduler:

            main()

            scheduler.assert_called_once_with(
                allowed_folder=self.workspace
            )

    def test_scheduler_loads_configured_workspace(self):
        schedule = {
            "name": "test_organizer",
            "workflow": "organize",
            "interval_minutes": 60,
            "enabled": True
        }

        with patch(
            "scheduler.scheduled_runner.load_config",
            return_value=self.settings
        ), patch(
            "scheduler.scheduled_runner.load_schedules",
            return_value=[schedule]
        ), patch(
            "scheduler.scheduled_runner.load_history",
            return_value={}
        ), patch(
            "scheduler.scheduled_runner.get_due_schedules",
            return_value=[schedule]
        ), patch(
            "scheduler.scheduled_runner.run_scheduled_workflow"
        ) as workflow, patch(
            "scheduler.scheduled_runner.save_history"
        ):

            result = run_due_schedules()

            workflow.assert_called_once_with(
                schedule, self.workspace
            )

            self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()