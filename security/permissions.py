from pathlib import Path
from config.config_loader import load_config


def is_action_allowed(action, allowed_folder=None):
    settings = load_config()

    if allowed_folder is None:
        allowed_folder = settings["allowed_folder"]

    try:
        allowed = Path(allowed_folder).resolve()

        source_path = Path(action["source"])
        destination_path = Path(action["destination"])

        if source_path.is_symlink() or destination_path.is_symlink():
            return False

        source = source_path.resolve()
        destination = destination_path.resolve()

        if not (
            allowed.is_dir()
            and source.is_relative_to(allowed)
            and destination.is_relative_to(allowed)
            and source.is_file()
            and not destination.exists()
        ):
            return False

        allowed_extensions = settings["allowed_extensions"]

        if source.suffix.lower() not in allowed_extensions:
            return False

        max_size_bytes = settings["max_file_size_mb"] * 1024 * 1024

        if source.stat().st_size > max_size_bytes:
            return False

        return True

    except (KeyError, TypeError, ValueError, OSError, RuntimeError):
        return False