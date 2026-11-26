import unittest
from unittest.mock import Mock, patch

from dashboard.app import SecureFlow


class TestDashboardPreview(unittest.TestCase):

    def setUp(self):
        self.app = Mock()
        self.app.pending = None
        self.app.menu.winfo_exists.return_value = True

        self.action = {
            "source": "test_files/example.txt",
            "destination": "test_files/txt/example.txt"
        }

    @patch("dashboard.app.run_workflow")
    def test_existing_preview_prevents_new_preview(self, run):
        self.app.pending = ([], "test_files", None)

        SecureFlow.preview(self.app, "organize")

        run.assert_not_called()

    @patch("dashboard.app.load_config")
    @patch("dashboard.app.Path.is_dir", return_value=False)
    def test_missing_workspace(self, is_dir, config):
        config.return_value = {"allowed_folder": "missing"}

        with self.assertRaises(ValueError):
            SecureFlow.preview(self.app, "organize")

    @patch("dashboard.app.load_config")
    @patch("dashboard.app.Path.is_dir", return_value=True)
    @patch("dashboard.app.run_workflow")
    @patch("dashboard.app.is_action_allowed", return_value=True)
    def test_allowed_action(self, allowed, run, is_dir, config):
        config.return_value = {"allowed_folder": "test_files"}
        run.return_value = [self.action]

        SecureFlow.preview(self.app, "organize")

        self.assertEqual(
            self.app.pending,
            ([self.action], "test_files", None)
        )
        self.app.approve.configure.assert_called_with(
            state="normal"
        )

    @patch("dashboard.app.load_config")
    @patch("dashboard.app.Path.is_dir", return_value=True)
    @patch("dashboard.app.run_workflow")
    @patch("dashboard.app.is_action_allowed", return_value=False)
    def test_blocked_action(self, allowed, run, is_dir, config):
        config.return_value = {"allowed_folder": "test_files"}
        run.return_value = [self.action]

        SecureFlow.preview(self.app, "organize")

        self.assertIsNone(self.app.pending)
        self.app.audit.assert_called_once_with(
            self.action, "BLOCKED", []
        )

    @patch("dashboard.app.load_config")
    @patch("dashboard.app.Path.is_dir", return_value=True)
    @patch("dashboard.app.run_workflow")
    @patch("dashboard.app.execute_action")
    def test_duplicate_detection_is_read_only(
        self, execute, run, is_dir, config
    ):
        config.return_value = {"allowed_folder": "test_files"}
        run.return_value = [{
            "original": "test_files/a.txt",
            "duplicate": "test_files/b.txt"
        }]

        SecureFlow.preview(self.app, "duplicates")

        execute.assert_not_called()
        self.assertIsNone(self.app.pending)
        self.app.write.assert_called_once_with(
            self.app.output,
            "Original: test_files/a.txt\n"
            "Duplicate: test_files/b.txt"
        )

    @patch("dashboard.app.load_config")
    @patch("dashboard.app.Path.is_dir", return_value=True)
    @patch("dashboard.app.run_workflow", return_value=[])
    def test_empty_workflow(self, run, is_dir, config):
        config.return_value = {"allowed_folder": "test_files"}

        SecureFlow.preview(self.app, "organize")

        self.assertIsNone(self.app.pending)
        self.app.write.assert_called_once_with(
            self.app.output,
            "0 permitted / 0 blocked"
        )


if __name__ == "__main__":
    unittest.main()