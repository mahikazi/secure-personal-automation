from pathlib import Path
from config.config_loader import load_config

def is_action_allowed(action, allowed_folder=None):
    if allowed_folder is None:
        settings = load_config()
        allowed_folder = settings["allowed_folder"]

    allowed = Path(allowed_folder).resolve()

    source_path = Path(action["source"])

    if source_path.is_symlink():
        return False

    source = Path(action["source"]).resolve()
    
    destination = Path(action["destination"]).resolve()

    if not (
        source.is_relative_to(allowed)
        and destination.is_relative_to(allowed)
        and source.is_file()
        and not source.is_symlink()
        and not destination.is_symlink()
        and not destination.exists()
    ):
        return False

    settings = load_config()

    allowed_extensions = settings["allowed_extensions"]

    if source.suffix.lower() not in allowed_extensions:
        return False

    max_size_bytes = settings["max_file_size_mb"] * 1024 * 1024

    if source.stat().st_size > max_size_bytes:
        return False

    return True