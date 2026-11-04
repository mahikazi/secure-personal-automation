import json
from pathlib import Path

def load_config():
    config_path = Path(__file__).parent / "settings.json"

    try:
        with config_path.open("r") as file:
            settings = json.load(file)

    except FileNotFoundError:
        raise ValueError("Configuration file is missing.")

    except json.JSONDecodeError:
        raise ValueError("Configuration file contains inavlid JSON.")

    if not isinstance(settings, dict):
        raise ValueError("Configuration must be a JSON object.")

    if not isinstance(settings.get("allowed_folder"), str) or not settings["allowed_folder"].strip():
        raise ValueError("Allowed folder must be a non-empty string.")

    extensions = settings.get("allowed_extensions")

    if not isinstance(extensions, list) or not extensions:
        raise ValueError("Allowed extensions must be a non-empty list.")

    if not all(
        isinstance(ext, str) and ext.startswith(".") and len(ext) > 1
        for ext in extensions
    ):
        raise ValueError("Every allowed extension must start with a dot.")

    max_size = settings.get("max_file_size_mb")

    if type(max_size) not in (int, float) or max_size <= 0:
        raise ValueError("Maximum file size must be a positive number.")

    return settings