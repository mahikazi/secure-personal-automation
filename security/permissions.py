from pathlib import Path

def is_action_allowed(action, allowed_folder):
    allowed = Path(allowed_folder).resolve()

    if Path(action["source"]).is_symlink():
        return False

    source = Path(action["source"]).resolve()
    destination = Path(action["destination"]).resolve()

    return (
        source.is_relative_to(allowed)
        and destination.is_relative_to(allowed)
        and source.is_file()
        and not source.is_symlink()
        and not destination.is_symlink()
        and not destination.exists()
    )