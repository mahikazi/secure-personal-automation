import json
import math
from pathlib import Path


def load_config():
    config_path = Path(__file__).parent / "settings.json"

    try:
        with config_path.open("r", encoding="utf-8") as file:
            settings = json.load(file)

    except FileNotFoundError:
        raise ValueError("Configuration file is missing.")

    except json.JSONDecodeError:
        raise ValueError("Configuration file contains invalid JSON.")

    if not isinstance(settings, dict):
        raise ValueError("Configuration must be a JSON object.")

    if (
        not isinstance(settings.get("allowed_folder"), str)
        or not settings["allowed_folder"].strip()
    ):
        raise ValueError("Allowed folder must be a non-empty string.")

    extensions = settings.get("allowed_extensions")

    if not isinstance(extensions, list) or not extensions:
        raise ValueError("Allowed extensions must be a non-empty list.")

    if not all(
        isinstance(ext, str)
        and ext.startswith(".")
        and len(ext) > 1
        and ext == ext.strip()
        and "/" not in ext
        and "\\" not in ext
        and "\x00" not in ext
        for ext in extensions
    ):
        raise ValueError("Invalid allowed file extension.")

    max_size = settings.get("max_file_size_mb")

    if (
        type(max_size) not in (int, float)
        or max_size <= 0
        or (
            isinstance(max_size, float)
            and not math.isfinite(max_size)
        )
    ):
        raise ValueError(
            "Maximum file size must be a finite positive number."
        )

    settings["allowed_extensions"] = [
        ext.lower() for ext in extensions
    ]

    return settings