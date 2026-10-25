import unittest

from security.permissions import is_action_allowed
from pathlib import Path
from tempfile import TemporaryDirectory

class TestPermissions(unittest.TestCase):
    def test_allows_safe_move(self):
        with TemporaryDirectory() as temp_dir:
            allowed_folder = Path(temp_dir)

            source = allowed_folder / "notes.txt"
            destination = allowed_folder / "organized" / "notes.txt"

            source.write_text("Hello!")

            action = {
                "source": source,
                "destination": destination
            }

            result = is_action_allowed(action, allowed_folder)

            self.assertTrue(result)

    def test_blocks_unauthorized_destination(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            allowed_folder = root / "allowed"
            allowed_folder.mkdir()

            source = allowed_folder / "notes.txt"
            source.write_text("Hello!")

            destination = root / "outside" / "notes.txt"

            action = {
                "source": source,
                "destination": destination
            }

            result = is_action_allowed(action, allowed_folder)

            self.assertFalse(result)

    def test_blocks_existing_destination(self):
        with TemporaryDirectory() as temp_dir:
            allowed_folder = Path(temp_dir)

            source = allowed_folder / "notes.txt"
            destination = allowed_folder / "existing.txt"

            source.write_text("Original file")
            destination.write_text("Important existing data")

            action = {
                "source": source,
                "destination": destination
            }

            result = is_action_allowed(action, allowed_folder)

            self.assertFalse(result)

    def test_blocks_path_traversal(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)

            allowed_folder = root / "alloweed"
            allowed_folder.mkdir()

            source = allowed_folder / "notes.txt"
            source.write_text("Hello!")

            destination = allowed_folder / ".." / "private" / "notes.txt"

            action = {
                "source": source,
                "destination": destination
            }

            result = is_action_allowed(action, allowed_folder)

            self.assertFalse(result)

    def test_blocks_symlink_destination(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
    
            allowed_folder = root / "allowed"
            allowed_folder.mkdir()

            private_folder = root / "private"
            private_folder.mkdir()

            source = allowed_folder / "notes.txt"
            source.write_text("Hello!")

            shortcut = allowed_folder / "shortcut"
            shortcut.symlink_to(private_folder, target_is_directory=True)

            destination = shortcut / "notes.txt"

            action = {
                "source": source,
                "destination": destination
            }
    
            result = is_action_allowed(action, allowed_folder)

            self.assertFalse(result)

    def test_blocks_symlink_source(self):
        with TemporaryDirectory() as temp_dir:
            allowed_folder = Path(temp_dir)
    
            real_file = allowed_folder / "notes.txt"
            real_file.write_text("Important data")

            shortcut = allowed_folder / "shortcut.txt"
            shortcut.symlink_to(real_file)

            destination = allowed_folder / "organized.txt"

            action = {
                "source": shortcut,
                "destination": destination
            }
    
            result = is_action_allowed(action, allowed_folder)

            self.assertFalse(result)
