import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from security.file_importer import import_files


class TestFileImporter(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace"
        self.external = self.root / "external"

        self.workspace.mkdir()
        self.external.mkdir()

        self.settings = {
            "allowed_folder": str(self.workspace),
            "allowed_extensions": [".txt", ".pdf"],
            "max_file_size_mb": 1
        }

        config_patch = patch(
            "security.file_importer.load_config",
            return_value=self.settings
        )

        config_patch.start()
        self.addCleanup(config_patch.stop)

        audit_patch = patch(
            "security.file_importer.log_action"
        )

        self.audit = audit_patch.start()
        self.addCleanup(audit_patch.stop)

    def create_file(self, name, content=b"Test content"):
        file = self.external / name
        file.write_bytes(content)
        return file

    def test_import_allowed_file(self):
        source = self.create_file("notes.txt")

        results = import_files([source])

        self.assertEqual(results[0]["status"], "SUCCESS")
        self.assertEqual(
            (self.workspace / source.name).read_bytes(),
            source.read_bytes()
        )

    def test_original_file_preserved(self):
        source = self.create_file("original.txt")
        original_content = source.read_bytes()

        import_files([source])

        self.assertTrue(source.exists())
        self.assertEqual(source.read_bytes(), original_content)

    def test_import_multiple_files(self):
        first = self.create_file("first.txt")
        second = self.create_file("second.pdf")

        results = import_files([first, second])

        self.assertEqual(len(results), 2)
        self.assertTrue(
            all(result["status"] == "SUCCESS" for result in results)
        )

    def test_block_disallowed_extension(self):
        source = self.create_file("program.exe")

        results = import_files([source])

        self.assertEqual(results[0]["status"], "BLOCKED")
        self.assertFalse((self.workspace / source.name).exists())

    def test_block_oversized_file(self):
        source = self.create_file(
            "large.txt",
            b"x" * (1024 * 1024 + 1)
        )

        results = import_files([source])

        self.assertEqual(results[0]["status"], "BLOCKED")
        self.assertFalse((self.workspace / source.name).exists())

    def test_prevent_overwrite(self):
        source = self.create_file("notes.txt", b"New content")
        destination = self.workspace / source.name
        destination.write_bytes(b"Existing content")

        results = import_files([source])

        self.assertEqual(results[0]["status"], "BLOCKED")
        self.assertEqual(destination.read_bytes(), b"Existing content")

    def test_block_symbolic_link(self):
        source = self.create_file("original.txt")
        link = self.external / "link.txt"

        try:
            link.symlink_to(source)
        except (OSError, NotImplementedError):
            self.skipTest("Symbolic links unavailable")

        results = import_files([link])

        self.assertEqual(results[0]["status"], "BLOCKED")
        self.assertFalse((self.workspace / link.name).exists())

    def test_block_missing_file(self):
        source = self.external / "missing.txt"

        results = import_files([source])

        self.assertEqual(results[0]["status"], "BLOCKED")

    def test_missing_workspace(self):
        self.settings["allowed_folder"] = str(
            self.root / "missing"
        )

        with self.assertRaises(ValueError):
            import_files([])

    def test_audit_successful_import(self):
        source = self.create_file("audit.txt")

        import_files([source])

        self.audit.assert_called_once_with(
            {
                "source": f"IMPORT: {source}",
                "destination": str(self.workspace.resolve() / source.name)
            },
            "SUCCESS"
        )

    def test_temporary_file_cleanup(self):
        source = self.create_file("cleanup.txt")

        import_files([source])

        self.assertEqual(
            list(self.workspace.glob(".import_*.tmp")),
            []
        )

    def test_failed_import_cleanup(self):
        source = self.create_file("failed.txt")

        with patch(
            "pathlib.Path.hardlink_to",
            side_effect=OSError("Simulated failure")
        ):
            results = import_files([source])

        self.assertEqual(results[0]["status"], "FAILED")
        self.assertTrue(source.exists())
        self.assertEqual(list(self.workspace.iterdir()), [])


if __name__ == "__main__":
    unittest.main()