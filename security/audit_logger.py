from datetime import datetime
from pathlib import Path


VALID_STATUSES = {
    "SUCCESS",
    "BLOCKED",
    "FAILED",
    "CANCELLED"
}


def sanitize_log_value(value):
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("\r", "\\r")
        .replace("\n", "\\n")
        .replace("\t", "\\t")
        .replace("|", "\\x7c")
    )


def log_action(action, status):
    if status not in VALID_STATUSES:
        raise ValueError("Invalid audit status.")

    log_file = Path("activity.log")
    timestamp = datetime.now().isoformat(timespec="seconds")

    source = sanitize_log_value(
        action.get("source", "<missing>")
        if isinstance(action, dict)
        else "<invalid action>"
    )

    destination = sanitize_log_value(
        action.get("destination", "<missing>")
        if isinstance(action, dict)
        else "<invalid action>"
    )

    with log_file.open("a", encoding="utf-8") as file:
        file.write(
            f"{timestamp} | {status} | "
            f"{source} -> {destination}\n"
        )