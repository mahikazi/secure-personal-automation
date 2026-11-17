import unittest
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory

from security.approval_executor import execute_approved_actions
from security.exceptions import FileOperationError

class TestApprovalExecutor(unittest.TestCase):

    def setUp(self):
        self.action = {
            "source": "test_files/notes.txt",
            "destination": "test_files/txt/notes.txt"
        }

    def test_approved_action_is_executed(self):
        with patch(
            "security.approval_executor.preview_actions",
            return_value=([self.action], [])
        ):
            with patch(
                "security.approval_executor.request_approval",
                return_value=True
            ):
                with patch(
                    "security.approval_executor.execute_action",
                    return_value=True
                ) as mock_execute:

                    result = execute_approved_actions(
                        [self.action],
                        "test_files"
                    )

        self.assertEqual(result, 1)
        mock_execute.assert_called_once_with(
            self.action,
            "test_files"
        )

    def test_rejected_action_is_not_executed(self):
        with patch(
            "security.approval_executor.preview_actions",
            return_value=([self.action], [])
        ):
            with patch(
                "security.approval_executor.request_approval",
                return_value=False
            ):
                with patch(
                    "security.approval_executor.execute_action"
                ) as mock_execute:
                    with patch(
                        "security.approval_executor.log_action"
                    ) as mock_log:

                        result = execute_approved_actions(
                            [self.action],
                            "test_files"
                        )

        self.assertEqual(result, 0)
        mock_execute.assert_not_called()
        mock_log.assert_called_once_with(
            self.action,
            "CANCELLED"
        )

    def test_blocked_action_is_not_executed(self):
        with patch(
            "security.approval_executor.preview_actions",
            return_value=([], [self.action])
        ):
            with patch(
                "security.approval_executor.request_approval"
            ) as mock_approval:
                with patch(
                    "security.approval_executor.execute_action"
                ) as mock_execute:
                    with patch(
                        "security.approval_executor.log_action"
                    ) as mock_log:

                        result = execute_approved_actions(
                            [self.action],
                            "test_files"
                        )

        self.assertEqual(result, 0)
        mock_approval.assert_not_called()
        mock_execute.assert_not_called()
        mock_log.assert_called_once_with(
            self.action,
            "BLOCKED"
        )

    def test_empty_workflow_is_not_executed(self):
        with patch(
            "security.approval_executor.execute_action"
        ) as mock_execute:
            with patch(
                "security.approval_executor.request_approval"
            ) as mock_approval:

                result = execute_approved_actions(
                    [],
                    "test_files"
                )

        self.assertEqual(result, 0)
        mock_execute.assert_not_called()
        mock_approval.assert_not_called()

    def test_execution_error_is_handled(self):
        with patch(
            "security.approval_executor.preview_actions",
            return_value=([self.action], [])
        ):
            with patch(
                "security.approval_executor.request_approval",
                return_value=True
            ):
                with patch(
                    "security.approval_executor.execute_action",
                    side_effect=FileOperationError(
                        "Simulated execution failure"
                    )
                ):

                    result = execute_approved_actions(
                        [self.action],
                        "test_files"
                    )

        self.assertEqual(result, 0)

    def test_cancelled_workflow_preserves_files(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / "notes.txt"
            destination = (
                Path(folder) / "organized" / "notes.txt"
            )

            source.write_text("Test content")

            action = {
                "source": str(source),
                "destination": str(destination)
            }

            with patch(
                "security.approval_executor.request_approval",
                return_value=False
            ):
                with patch(
                    "security.approval_executor.log_action"
                ):

                    result = execute_approved_actions(
                        [action],
                        folder
                    )

            self.assertEqual(result, 0)
            self.assertTrue(source.exists())
            self.assertFalse(destination.exists())
            self.assertFalse(destination.parent.exists())

    def test_approved_workflow_moves_file(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / "notes.txt"
            destination = (
                Path(folder) / "organized" / "notes.txt"
            )

            source.write_text("Test content")

            action = {
                "source": str(source),
                "destination": str(destination)
            }

            with patch(
                "security.approval_executor.request_approval",
                return_value=True
            ):
                with patch(
                    "security.executor.log_action"
                ):

                    result = execute_approved_actions(
                        [action],
                        folder
                    )

            self.assertEqual(result, 1)
            self.assertFalse(source.exists())
            self.assertTrue(destination.exists())
            self.assertEqual(
                destination.read_text(),
                "Test content"
            )


if __name__ == "__main__":
    unittest.main()