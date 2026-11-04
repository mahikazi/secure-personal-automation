import unittest
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory

from security.executor import execute_action
from security.exceptions import FileOperationError

class TestExecutor(unittest.TestCase):

    def test_handles_filesystem_error(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / "notes.txt"
            destination = Path(folder) / "organized" / "notes.txt"

            source.write_text("Test content")

            action = {
                "source": str(source),
                "destination": str(destination)
            }

            with patch("security.executor.is_action_allowed", return_value=True):
                with patch(
                    "pathlib.Path.hardlink_to",
                    side_effect=OSError("Simulated disk error")
                ):
                    with patch("security.executor.log_action"):
                        with self.assertRaises(FileOperationError):
                            execute_action(action, folder)

    def test_handles_source_deletion_failure(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / "notes.txt"
            destination = Path(folder) / "organized" / "notes.txt"
        
            source.write_text("Test content")
        
            action = {
                "source": str(source),
                "destination": str(destination)
            }
        
            with patch("security.executor.is_action_allowed", return_value=True):
                with patch("security.executor.log_action"):
                    with patch(
                        "pathlib.Path.unlink",
                        side_effect=PermissionError("Deletion denied")
                    ):
                        with self.assertRaises(FileOperationError):
                            execute_action(action, folder)

            self.assertTrue(source.exists())
            self.assertTrue(destination.exists())

    def test_preserves_file_error_when_audit_logging_fails(self):
        with TemporaryDirectory() as folder:
            source = Path(folder) / "notes.txt"
            destination = Path(folder) / "organized" / "notes.txt"
        
            source.write_text("Test content")
        
            action = {
                "source": str(source),
                "destination": str(destination)
            }
        
            with patch("security.executor.is_action_allowed", return_value=True):
                with patch("pathlib.Path.hardlink_to", side_effect=OSError("Simulated disk error")):
                    with patch(
                        "security.executor.log_action",
                        side_effect=OSError("Simulated audit-log error")
                    ):
                        with self.assertRaises(FileOperationError) as context:
                            execute_action(action, folder)

            self.assertIn("Simulated disk error", str(context.exception))