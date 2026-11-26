import json
import os
import tempfile

from datetime import datetime, timezone
from pathlib import Path


DEFAULT_HISTORY_PATH = Path("logs/schedule_history.json")


def load_history(history_path=DEFAULT_HISTORY_PATH):
    history_path = Path(history_path)

    if not history_path.exists():
        return {}

    with history_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Schedule history must be a JSON object.")

    history = {}

    for name, timestamp in data.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Invalid schedule history name.")

        if not isinstance(timestamp, str):
            raise ValueError("Invalid schedule history timestamp.")

        parsed = datetime.fromisoformat(timestamp)

        if parsed.tzinfo is None:
            raise ValueError(
                "Schedule history timestamps must include a timezone."
            )

        history[name] = parsed.astimezone(timezone.utc)

    return history


def save_history(last_runs, history_path=DEFAULT_HISTORY_PATH):
    history_path = Path(history_path)

    history_path.parent.mkdir(parents=True, exist_ok=True)

    serialized = {}

    for name, timestamp in last_runs.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Invalid schedule history name.")

        if (
            not isinstance(timestamp, datetime)
            or timestamp.utcoffset() is None
        ):
            raise ValueError(
                "Schedule history timestamps must include a timezone."
            )

        serialized[name] = timestamp.astimezone(
            timezone.utc
        ).isoformat()

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=history_path.parent,
            prefix=".schedule_history_",
            suffix=".tmp",
            delete=False
        ) as file:
            temporary_path = Path(file.name)

            json.dump(serialized, file, indent=2)

            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary_path, history_path)

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)