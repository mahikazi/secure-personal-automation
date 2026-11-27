import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from dashboard.app import SecureFlow


class TestDashboardWorkspace(unittest.TestCase):
    def setUp(self):
        self.app = Mock(spec=SecureFlow)

        self.workspace = Path.cwd() / "test_files"

        self.settings = {
            "allowed_folder": str(self.workspace),
            "allowed_extensions": [".txt", ".pdf"],
            "max_file_size_mb": 20
        }

    @patch("dashboard.app.save_config")
    @patch("dashboard.app.load_config")
    @patch("dashboard.app.messagebox.askyesno")
    @patch("dashboard.app.filedialog.askdirectory")
    def test_choose_workspace(
        self, picker, confirm, load, save
    ):
        picker.return_value = str(self.workspace)
        confirm.return_value = True
        load.return_value = dict(self.settings)

        SecureFlow.choose_workspace(self.app)

        save.assert_called_once_with(self.settings)
        self.app.navigate.assert_called_once_with("Workspace")

    @patch("dashboard.app.save_config")
    @patch("dashboard.app.filedialog.askdirectory")
    def test_cancel_workspace_picker(self, picker, save):
        picker.return_value = ""

        SecureFlow.choose_workspace(self.app)

        save.assert_not_called()
        self.app.navigate.assert_not_called()

    @patch("dashboard.app.save_config")
    @patch("dashboard.app.messagebox.askyesno")
    @patch("dashboard.app.filedialog.askdirectory")
    def test_reject_workspace_change(
        self, picker, confirm, save
    ):
        picker.return_value = str(self.workspace)
        confirm.return_value = False

        SecureFlow.choose_workspace(self.app)

        save.assert_not_called()

    @patch("dashboard.app.messagebox.showinfo")
    @patch("dashboard.app.import_files")
    @patch("dashboard.app.messagebox.askyesno")
    @patch("dashboard.app.filedialog.askopenfilenames")
    @patch("dashboard.app.get_workspace")
    def test_approved_file_import(
        self, workspace, picker, confirm, importer, info
    ):
        workspace.return_value = self.workspace
        picker.return_value = ("notes.txt",)
        confirm.return_value = True

        importer.return_value = [
            {
                "filename": "notes.txt",
                "status": "SUCCESS",
                "message": "File imported successfully."
            }
        ]

        SecureFlow.import_workspace_files(self.app)

        importer.assert_called_once_with(("notes.txt",))
        self.app.refresh_workspace.assert_called_once()
        info.assert_called_once()

    @patch("dashboard.app.import_files")
    @patch("dashboard.app.filedialog.askopenfilenames")
    @patch("dashboard.app.get_workspace")
    def test_cancel_file_picker(
        self, workspace, picker, importer
    ):
        workspace.return_value = self.workspace
        picker.return_value = ()

        SecureFlow.import_workspace_files(self.app)

        importer.assert_not_called()

    @patch("dashboard.app.import_files")
    @patch("dashboard.app.messagebox.askyesno")
    @patch("dashboard.app.filedialog.askopenfilenames")
    @patch("dashboard.app.get_workspace")
    def test_reject_file_import(
        self, workspace, picker, confirm, importer
    ):
        workspace.return_value = self.workspace
        picker.return_value = ("notes.txt",)
        confirm.return_value = False

        SecureFlow.import_workspace_files(self.app)

        importer.assert_not_called()

    @patch("dashboard.app.messagebox.showerror")
    @patch("dashboard.app.import_files")
    @patch("dashboard.app.messagebox.askyesno")
    @patch("dashboard.app.filedialog.askopenfilenames")
    @patch("dashboard.app.get_workspace")
    def test_changed_workspace_blocks_import(
        self, workspace, picker, confirm, importer, error
    ):
        workspace.side_effect = [
            self.workspace,
            self.workspace / "different"
        ]

        picker.return_value = ("notes.txt",)
        confirm.return_value = True

        SecureFlow.import_workspace_files(self.app)

        importer.assert_not_called()
        error.assert_called_once()

    @patch("dashboard.app.list_workspace_files")
    def test_refresh_empty_workspace(self, files):
        files.return_value = []

        self.app.workspace_count = Mock()
        self.app.workspace_box = Mock()

        SecureFlow.refresh_workspace(self.app)

        self.app.workspace_count.configure.assert_called_once_with(
            text="0 files · 0 B"
        )

        self.app.write.assert_called_once_with(
            self.app.workspace_box,
            "Your workspace is empty. Import files to begin."
        )

    @patch("dashboard.app.messagebox.showinfo")
    @patch("dashboard.app.save_config")
    @patch("dashboard.app.load_config")
    @patch("dashboard.app.messagebox.askyesno")
    def test_save_security_settings(
        self, confirm, load, save, info
    ):
        confirm.return_value = True
        load.return_value = dict(self.settings)

        self.app.extensions_entry = Mock()
        self.app.extensions_entry.get.return_value = ".txt, .pdf, .csv"

        self.app.size_entry = Mock()
        self.app.size_entry.get.return_value = "50"

        SecureFlow.save_settings(self.app)

        save.assert_called_once_with({
            "allowed_folder": str(self.workspace),
            "allowed_extensions": [".txt", ".pdf", ".csv"],
            "max_file_size_mb": 50.0
        })

        self.app.navigate.assert_called_once_with("Settings")

    @patch("dashboard.app.save_config")
    @patch("dashboard.app.load_config")
    @patch("dashboard.app.messagebox.askyesno")
    def test_reject_security_settings(
        self, confirm, load, save
    ):
        confirm.return_value = False
        load.return_value = dict(self.settings)

        self.app.extensions_entry = Mock()
        self.app.extensions_entry.get.return_value = ".txt"

        self.app.size_entry = Mock()
        self.app.size_entry.get.return_value = "50"

        SecureFlow.save_settings(self.app)

        save.assert_not_called()

    @patch("dashboard.app.messagebox.showerror")
    @patch("dashboard.app.save_config")
    @patch("dashboard.app.load_config")
    def test_invalid_size_setting(self, load, save, error):
        load.return_value = dict(self.settings)

        self.app.extensions_entry = Mock()
        self.app.extensions_entry.get.return_value = ".txt"

        self.app.size_entry = Mock()
        self.app.size_entry.get.return_value = "invalid"

        SecureFlow.save_settings(self.app)

        save.assert_not_called()
        error.assert_called_once()


if __name__ == "__main__":
    unittest.main()