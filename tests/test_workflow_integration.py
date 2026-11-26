import os
import time
import unittest
import tempfile

from pathlib import Path
from unittest.mock import patch

from workflows.workflow_manager import run_workflow
from security.approval_executor import execute_approved_actions


class TestWorkflowIntegration(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.workspace = Path(self.temp.name).resolve()

        self.source = self.workspace / "example.txt"
        self.source.write_text("SecureFlow integration test")

        self.settings = {
            "allowed_folder": str(self.workspace),
            "allowed_extensions": [".txt"],
            "max_file_size_mb": 20
        }

        config = patch(
            "security.permissions.load_config",
            return_value=self.settings
        )

        config.start()
        self.addCleanup(config.stop)

        for target in (
            "security.executor.log_action",
            "security.approval_executor.log_action"
        ):
            logger = patch(target)
            logger.start()
            self.addCleanup(logger.stop)

    @patch(
        "security.approval_executor.request_approval",
        return_value=True
    )
    def test_organizer_to_secure_execution(self, approve):
        actions = run_workflow("organize", self.workspace)

        result = execute_approved_actions(
            actions, self.workspace
        )

        destination = self.workspace / "txt" / "example.txt"

        self.assertEqual(result, 1)
        self.assertFalse(self.source.exists())
        self.assertTrue(destination.exists())
        self.assertEqual(
            destination.read_text(),
            "SecureFlow integration test"
        )

    @patch(
        "security.approval_executor.request_approval",
        return_value=False
    )
    def test_organizer_cancellation(self, approve):
        actions = run_workflow("organize", self.workspace)

        result = execute_approved_actions(
            actions, self.workspace
        )

        self.assertEqual(result, 0)
        self.assertTrue(self.source.exists())
        self.assertFalse(
            (self.workspace / "txt" / "example.txt").exists()
        )

    @patch(
        "security.approval_executor.request_approval",
        return_value=True
    )
    def test_archiver_to_secure_execution(self, approve):
        old_time = time.time() - (60 * 24 * 60 * 60)

        os.utime(self.source, (old_time, old_time))

        actions = run_workflow(
            "archive", self.workspace, 30
        )

        result = execute_approved_actions(
            actions, self.workspace
        )

        self.assertEqual(result, 1)
        self.assertFalse(self.source.exists())
        self.assertTrue(
            (self.workspace / "archive" / "example.txt").exists()
        )

    def test_organizer_skips_symlinks(self):
        link = self.workspace / "link.txt"
        link.symlink_to(self.source)

        actions = run_workflow("organize", self.workspace)

        sources = [
            Path(action["source"]) for action in actions
        ]

        self.assertIn(self.source, sources)
        self.assertNotIn(link, sources)

    def test_archiver_skips_symlinks(self):
        old_time = time.time() - (60 * 24 * 60 * 60)

        os.utime(self.source, (old_time, old_time))

        link = self.workspace / "link.txt"
        link.symlink_to(self.source)

        actions = run_workflow(
            "archive", self.workspace, 30
        )

        sources = [
            Path(action["source"]) for action in actions
        ]

        self.assertIn(self.source, sources)
        self.assertNotIn(link, sources)


if __name__ == "__main__":
    unittest.main()