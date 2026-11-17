import unittest
from unittest.mock import patch

from security.approval import request_approval

class TestApproval(unittest.TestCase):

    def test_user_approves_actions(self):
        with patch("builtins.input", return_value="y"):
            result = request_approval(2)

        self.assertTrue(result)

    def test_user_rejects_actions(self):
        with patch("builtins.input", return_value="n"):
            result = request_approval(2)

        self.assertFalse(result)

    def test_invalid_input_requests_again(self):
        with patch(
            "builtins.input",
            side_effect=["invalid", "yes"]
        ):
            result = request_approval(2)

        self.assertTrue(result)

    def test_no_actions_cannot_be_approved(self):
        with patch("builtins.input") as mock_input:
            result = request_approval(0)

        self.assertFalse(result)
        mock_input.assert_not_called()

if __name__ == "__main__":
    unittest.main()