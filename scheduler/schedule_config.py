import json
from pathlib import Path

DEFAULT_SCHEDULE_PATH = Path("config/schedules.json")
ALLOWED_WORKFLOWS = {"organize", "archive", "duplicates"}

def load_schedules(config_path=DEFAULT_SCHEDULE_PATH):
    config_path = Path(config_path)

    with config_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError("Schedule configuration must be a JSON object.")

    schedules = data.get("schedules")

    if not isinstance(schedules, list):
        raise ValueError("'schedules' must be a list.")

    names = set()

    for schedule in schedules:
        if not isinstance(schedule, dict):
            raise ValueError("Each schedule must be a JSON object.")

        name = schedule.get("name")
        workflow = schedule.get("workflow")
        interval = schedule.get("interval_minutes")
        enabled = schedule.get("enabled")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Schedule namesm ust be non-empty strings.")

        if name in names:
            raise ValueError(f"Duplicate schedule name: {name}")

        names.add(name)

        if workflow not in ALLOWED_WORKFLOWS:
            raise ValueError(f"Unsupported workflow: {workflow}")

        if type(interval) is not int or interval <= 0:
            raise ValueError(
                "Schedule intervals must be positive whole numbers."
            )

        if type(enabled) is not bool:
            raise ValueError("'enabled' must be true or false.")

        if workflow == "archive":
            days_old = schedule.get("days_old")

            if type(days_old) is not int or days_old <= 0:
                raise ValueError(
                    "Archive schedules require positive 'days_old'."
                )
    return schedules