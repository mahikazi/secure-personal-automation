import json
import math
import os
import tempfile
from pathlib import Path


CONFIG_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = CONFIG_DIR / "settings.json"
LOCAL_CONFIG = CONFIG_DIR / "settings.local.json"


def validate_config(settings):
    if not isinstance(settings, dict):
        raise ValueError("Configuration must be a JSON object.")

    if (
        not isinstance(settings.get("allowed_folder"), str)
        or not settings["allowed_folder"].strip()
        or "\x00" in settings["allowed_folder"]
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

    validated = dict(settings)

    validated["allowed_extensions"] = list(
        dict.fromkeys(ext.lower() for ext in extensions)
    )

    return validated


def load_config():
    config_path = (
        LOCAL_CONFIG
        if LOCAL_CONFIG.exists()
        else DEFAULT_CONFIG
    )

    try:
        with config_path.open("r", encoding="utf-8") as file:
            settings = json.load(file)

    except FileNotFoundError:
        raise ValueError("Configuration file is missing.")

    except json.JSONDecodeError:
        raise ValueError("Configuration file contains invalid JSON.")

    return validate_config(settings)


def save_config(settings):
    validated = validate_config(settings)

    workspace = Path(
        validated["allowed_folder"]
    ).expanduser().resolve()

    if not workspace.is_dir():
        raise ValueError(
            "Selected workspace must be an existing directory."
        )

    validated["allowed_folder"] = str(workspace)

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=CONFIG_DIR,
            prefix=".settings_",
            suffix=".tmp",
            delete=False
        ) as file:
            temporary_path = Path(file.name)

            json.dump(
                validated,
                file,
                indent=2,
                allow_nan=False
            )

            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary_path, LOCAL_CONFIG)

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return validated