import unittest
from unittest.mock import Mock, patch

from dashboard.app import SecureFlow


class TestDashboardExecution(unittest.TestCase):

    def setUp(self):
        self.app = Mock()

        self.action = {
            "source": "test_files/example.txt",
            "destination": "test_files/txt/example.txt"
        }

        self.app.pending = (
            [self.action],
            "test_files",
            None
        )

    @patch("dashboard.app.execute_action")
    @patch("dashboard.app.messagebox.askyesno")
    def test_execution_without_preview(self, confirm, execute):
        self.app.pending = None

        SecureFlow.execute(self.app)

        confirm.assert_not_called()
        execute.assert_not_called()

    @patch("dashboard.app.execute_action")
    @patch("dashboard.app.messagebox.askyesno", return_value=False)
    def test_execution_without_confirmation(self, confirm, execute):
        SecureFlow.execute(self.app)

        execute.assert_not_called()
        self.app.reset_preview.assert_not_called()

    @patch("dashboard.app.load_config")
    @patch("dashboard.app.execute_action", return_value=True)
    @patch("dashboard.app.messagebox.askyesno", return_value=True)
    def test_approved_execution(self, confirm, execute, config):
        config.return_value = {
            "allowed_folder": "test_files"
        }

        SecureFlow.execute(self.app)

        execute.assert_called_once_with(
            self.action, "test_files"
        )
        self.app.reset_preview.assert_called_once()

        result = self.app.write.call_args.args[1]
        self.assertIn("1 of 1 files moved.", result)

    @patch("dashboard.app.load_config")
    @patch("dashboard.app.execute_action")
    @patch("dashboard.app.messagebox.askyesno", return_value=True)
    def test_changed_workspace_blocks_execution(
        self, confirm, execute, config
    ):
        config.return_value = {
            "allowed_folder": "different_folder"
        }

        SecureFlow.execute(self.app)

        execute.assert_not_called()

        result = self.app.write.call_args.args[1]
        self.assertIn("Workspace configuration changed", result)

    @patch("dashboard.app.execute_action")
    def test_cancelled_execution(self, execute):
        SecureFlow.cancel(self.app)

        execute.assert_not_called()

        self.app.audit.assert_called_once_with(
            self.action, "CANCELLED", []
        )
        self.app.reset_preview.assert_called_once()

    @patch("dashboard.app.load_config")
    @patch("dashboard.app.execute_action")
    @patch("dashboard.app.messagebox.askyesno", return_value=True)
    def test_execution_failure(self, confirm, execute, config):
        config.return_value = {
            "allowed_folder": "test_files"
        }

        execute.side_effect = OSError("File operation failed")

        SecureFlow.execute(self.app)

        self.app.reset_preview.assert_called_once()

        result = self.app.write.call_args.args[1]
        self.assertIn("0 of 1 files moved.", result)
        self.assertIn("File operation failed", result)


if __name__ == "__main__":
    unittest.main()