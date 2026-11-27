import tempfile
import unittest
from pathlib import Path

from workflows.duplicate_detector import detect_duplicates


class TestDuplicateDetector(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_identical_files_are_detected(self):
        first = self.folder / "first.txt"
        second = self.folder / "second.txt"

        first.write_text("Identical content")
        second.write_text("Identical content")

        duplicates = detect_duplicates(self.folder)

        self.assertEqual(len(duplicates), 1)
        self.assertEqual(
            {
                duplicates[0]["original"],
                duplicates[0]["duplicate"]
            },
            {first, second}
        )

    def test_different_files_are_not_duplicates(self):
        (self.folder / "first.txt").write_text("First")
        (self.folder / "second.txt").write_text("Other")

        self.assertEqual(detect_duplicates(self.folder), [])

    def test_symbolic_links_are_ignored(self):
        original = self.folder / "original.txt"
        original.write_text("Example content")

        link = self.folder / "link.txt"
        link.symlink_to(original)

        self.assertEqual(detect_duplicates(self.folder), [])

    def test_nested_files_are_ignored(self):
        (self.folder / "original.txt").write_text("Example")

        nested = self.folder / "nested"
        nested.mkdir()

        (nested / "duplicate.txt").write_text("Example")

        self.assertEqual(detect_duplicates(self.folder), [])

    def test_duplicate_detection_is_read_only(self):
        first = self.folder / "first.txt"
        second = self.folder / "second.txt"

        first.write_text("Example content")
        second.write_text("Example content")

        before = {
            file.name: (file.read_bytes(), file.stat().st_mtime_ns)
            for file in self.folder.iterdir()
        }

        duplicates = detect_duplicates(self.folder)

        after = {
            file.name: (file.read_bytes(), file.stat().st_mtime_ns)
            for file in self.folder.iterdir()
        }

        self.assertEqual(len(duplicates), 1)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()