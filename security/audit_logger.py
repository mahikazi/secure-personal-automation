from datetime import datetime
from pathlib import Path

def log_action(action, status):
    log_file = Path("activity.log")
    timestamp = datetime.now().isoformat(timespec="seconds")

    with log_file.open("a") as file:
        file.write(
            f"{timestamp} | {status} | "
            f"{action['source']} -> {action['destination']}\n"
        )