import os
from pathlib import Path

from config.config_loader import load_config


def get_workspace():
    settings = load_config()

    workspace = Path(
        settings["allowed_folder"]
    ).resolve()

    if not workspace.is_dir():
        raise ValueError("Workspace does not exist.")

    return workspace


def list_workspace_files():
    workspace = get_workspace()
    files = []

    for folder, directories, filenames in os.walk(
        workspace,
        followlinks=False
    ):
        current_folder = Path(folder)

        directories[:] = sorted(
            name for name in directories
            if not (current_folder / name).is_symlink()
            and not name.startswith(".")
        )

        for filename in sorted(filenames):
            file = current_folder / filename

            try:
                if filename.startswith("."):
                    continue

                if file.is_symlink() or not file.is_file():
                    continue

                if not file.resolve().is_relative_to(workspace):
                    continue

                files.append({
                    "name": file.name,
                    "path": str(file),
                    "relative_path": str(
                        file.relative_to(workspace)
                    ),
                    "extension": file.suffix.lower() or "None",
                    "size": file.stat().st_size
                })

            except (OSError, RuntimeError, ValueError):
                continue

    return sorted(
        files,
        key=lambda file: file["relative_path"].lower()
    )


def format_file_size(size):
    value = float(size)

    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(value)} {unit}"

            return f"{value:.1f} {unit}"

        value /= 1024