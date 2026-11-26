import unittest
import tempfile

from pathlib import Path
from unittest.mock import patch

from security.permissions import is_action_allowed
from security.executor import execute_action
from security.exceptions import FileOperationError


class TestSecurityHardening(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()

        self.source = self.workspace / "example.txt"
        self.source.write_text("SecureFlow test")

        self.destination = self.workspace / "txt" / "example.txt"

        self.action = {
            "source": self.source,
            "destination": self.destination
        }

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

    def test_dangling_destination_symlink(self):
        self.destination.parent.mkdir()
        self.destination.symlink_to(
            self.workspace / "missing.txt"
        )

        self.assertFalse(
            is_action_allowed(self.action, self.workspace)
        )

    def test_source_symlink_rejected(self):
        link = self.workspace / "link.txt"
        link.symlink_to(self.source)

        self.action["source"] = link

        self.assertFalse(
            is_action_allowed(self.action, self.workspace)
        )

    def test_destination_parent_symlink_escape(self):
        outside = self.root / "outside"
        outside.mkdir()

        link = self.workspace / "redirect"
        link.symlink_to(outside, target_is_directory=True)

        self.action["destination"] = link / "example.txt"

        self.assertFalse(
            is_action_allowed(self.action, self.workspace)
        )

    def test_malformed_action_rejected(self):
        for action in ({}, None, [], {"source": self.source}):
            with self.subTest(action=action):
                self.assertFalse(
                    is_action_allowed(action, self.workspace)
                )

    def test_missing_workspace_rejected(self):
        missing = self.root / "missing"

        self.assertFalse(
            is_action_allowed(self.action, missing)
        )

    @patch("security.executor.log_action")
    def test_partial_move_failure(self, log):
        with patch.object(
            Path,
            "unlink",
            side_effect=PermissionError("Removal denied")
        ):
            with self.assertRaises(FileOperationError) as error:
                execute_action(self.action, self.workspace)

        self.assertIn(
            "source removal failed",
            str(error.exception)
        )

        self.assertTrue(self.source.exists())
        self.assertTrue(self.destination.exists())

        log.assert_called_once_with(self.action, "FAILED")


if __name__ == "__main__":
    unittest.main()