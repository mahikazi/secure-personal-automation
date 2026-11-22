from datetime import datetime, timedelta, timezone

def current_time():
    return datetime.now(timezone.utc)

def is_schedule_due(schedule, last_run=None, now=None):
    if not schedule["enabled"]:
        return False

    if now is None:
        now = current_time()

    if last_run is None:
        return True

    interval = timedelta(minutes=schedule["interval_minutes"])

    return now >= last_run + interval

def get_due_schedules(schedules, last_runs=None, now=None):
    if last_runs is None:
        last_runs = {}

    if now is None:
        now = current_time()

    due_schedules = []

    for schedule in schedules:
        last_run = last_runs.get(schedule["name"])

        if is_schedule_due(schedule, last_run, now):
            due_schedules.append(schedule)

    return due_schedules