import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from workflows.workspace_browser import (
    get_workspace,
    list_workspace_files,
    format_file_size
)


class TestWorkspaceBrowser(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.root = Path(self.temp.name).resolve()
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()

        self.settings = {
            "allowed_folder": str(self.workspace),
            "allowed_extensions": [".txt", ".pdf"],
            "max_file_size_mb": 20
        }

        config_patch = patch(
            "workflows.workspace_browser.load_config",
            return_value=self.settings
        )

        config_patch.start()
        self.addCleanup(config_patch.stop)

    def test_get_workspace(self):
        self.assertEqual(get_workspace(), self.workspace)

    def test_missing_workspace(self):
        self.settings["allowed_folder"] = str(
            self.root / "missing"
        )

        with self.assertRaises(ValueError):
            get_workspace()

    def test_empty_workspace(self):
        self.assertEqual(list_workspace_files(), [])

    def test_list_workspace_files(self):
        (self.workspace / "notes.txt").write_text("Hello")
        (self.workspace / "document.pdf").write_bytes(b"PDF")

        files = list_workspace_files()

        self.assertEqual(len(files), 2)
        self.assertEqual(
            {file["name"] for file in files},
            {"notes.txt", "document.pdf"}
        )

    def test_nested_files(self):
        folder = self.workspace / "documents"
        folder.mkdir()

        (folder / "notes.txt").write_text("Hello")

        files = list_workspace_files()

        self.assertEqual(len(files), 1)
        self.assertEqual(
            files[0]["relative_path"],
            str(Path("documents") / "notes.txt")
        )

    def test_file_metadata(self):
        source = self.workspace / "notes.TXT"
        source.write_bytes(b"Hello")

        files = list_workspace_files()

        self.assertEqual(files[0]["name"], "notes.TXT")
        self.assertEqual(files[0]["extension"], ".txt")
        self.assertEqual(files[0]["size"], 5)
        self.assertEqual(files[0]["path"], str(source))

    def test_hidden_files_are_ignored(self):
        (self.workspace / ".hidden.txt").write_text("Hidden")
        (self.workspace / "visible.txt").write_text("Visible")

        files = list_workspace_files()

        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["name"], "visible.txt")

    def test_hidden_directories_are_ignored(self):
        folder = self.workspace / ".hidden"
        folder.mkdir()

        (folder / "notes.txt").write_text("Hidden")

        self.assertEqual(list_workspace_files(), [])

    def test_symbolic_links_are_ignored(self):
        external = self.root / "external.txt"
        external.write_text("External content")

        link = self.workspace / "link.txt"

        try:
            link.symlink_to(external)
        except (OSError, NotImplementedError):
            self.skipTest("Symbolic links unavailable")

        self.assertEqual(list_workspace_files(), [])

    def test_symbolic_link_directories_are_ignored(self):
        external = self.root / "external"
        external.mkdir()

        (external / "notes.txt").write_text("External")

        link = self.workspace / "linked_folder"

        try:
            link.symlink_to(external, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symbolic links unavailable")

        self.assertEqual(list_workspace_files(), [])

    def test_files_are_sorted(self):
        for name in ["zebra.txt", "apple.txt", "middle.txt"]:
            (self.workspace / name).write_text("Content")

        files = list_workspace_files()

        self.assertEqual(
            [file["name"] for file in files],
            ["apple.txt", "middle.txt", "zebra.txt"]
        )

    def test_browser_preserves_files(self):
        source = self.workspace / "notes.txt"
        source.write_bytes(b"Original content")

        list_workspace_files()

        self.assertTrue(source.exists())
        self.assertEqual(
            source.read_bytes(),
            b"Original content"
        )

    def test_format_file_size(self):
        self.assertEqual(format_file_size(0), "0 B")
        self.assertEqual(format_file_size(500), "500 B")
        self.assertEqual(format_file_size(1024), "1.0 KB")
        self.assertEqual(format_file_size(1536), "1.5 KB")
        self.assertEqual(format_file_size(1024 ** 2), "1.0 MB")
        self.assertEqual(format_file_size(1024 ** 3), "1.0 GB")
        self.assertEqual(format_file_size(1024 ** 4), "1.0 TB")


if __name__ == "__main__":
    unittest.main()