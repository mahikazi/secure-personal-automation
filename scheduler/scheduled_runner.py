from scheduler.schedule_config import load_schedules
from scheduler.schedule_manager import (
    current_time,
    get_due_schedules,
)
from scheduler.schedule_history import (
    load_history,
    save_history
)
from workflows.workflow_manager import run_workflow
from security.approval_executor import execute_approved_actions

def run_scheduled_workflow(schedule, allowed_folder):
    workflow = schedule["workflow"]

    if workflow == "archive":
        actions = run_workflow(
            workflow,
            allowed_folder,
            schedule["days_old"]
        )
    else:
        actions = run_workflow(workflow, allowed_folder)

    if workflow == "duplicates":
        if not actions:
            print("No duplicates found.")

        for pair in actions:
            print(f"Original: {pair['original']}")
            print(f"Duplicate: {pair['duplicate']}")

        return 0

    return execute_approved_actions(actions, allowed_folder)

def run_due_schedules(
        allowed_folder="test_files",
        config_path="config/schedules.json",
        history_path="logs/schedule_history.json",
        now=None
    ):

        if now is None:
            now = current_time()

        schedules = load_schedules(config_path)
        last_runs = load_history(history_path)

        due_schedules = get_due_schedules(
            schedules,
            last_runs,
            now
        )

        if not due_schedules:
            print("No scheduled workflows are due.")
            return 0

        completed = 0

        for schedule in due_schedules:
            print(f"\nScheduled workflow: {schedule['name']}")

            run_scheduled_workflow(schedule, allowed_folder)

            last_runs[schedule["name"]] = now
            save_history(last_runs, history_path)

            completed += 1

        print(f"\nScheduled workflows processed: {completed}")

        return completed