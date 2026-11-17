import unittest
from unittest.mock import patch

from security.preview import preview_action
from security.preview import preview_actions

class TestPreview(unittest.TestCase):

    def setUp(self):
        self.action = {
            "source": "test_files/notes.txt",
            "destination": "test_files/txt/notes.txt"
        }

    def test_preview_allows_permitted_action(self):
        with patch(
            "security.preview.is_action_allowed",
            return_value=True
        ):
            result = preview_action(
                self.action,
                "test_files"
            )

        self.assertTrue(result)

    def test_preview_blocks_unauthorized_action(self):
        with patch(
            "security.preview.is_action_allowed",
            return_value = False
        ):
            result = preview_action(
                self.action,
                "test_files"
            )

        self.assertFalse(result)

    def test_preview_separates_allowed_and_blocked_actions(self):
        blocked_action = {
            "source": "test_files/program.exe",
            "destination": "test_files/exe/program.exe"
        }

        actions = [
            self.action,
            blocked_action
        ]

        with patch(
            "security.preview.is_action_allowed",
            side_effect=[True, False]
        ):
            allowed, blocked = preview_actions(
                actions,
                "test_files"
            )

        self.assertEqual(allowed, [self.action])
        self.assertEqual(blocked, [blocked_action])

if __name__ == "__main__":
    unittest.main()