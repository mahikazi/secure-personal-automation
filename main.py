from pathlib import Path

from config.config_loader import load_config
from scheduler.scheduled_runner import run_due_schedules
from workflows.workflow_manager import run_workflow
from security.approval_executor import execute_approved_actions


def main():
    try:
        settings = load_config()
        allowed_folder = settings["allowed_folder"]

        if not Path(allowed_folder).is_dir():
            print(f"ERROR: Workspace does not exist: {allowed_folder}")
            return

        print("Secure Personal Automation Platform")
        print("System initialized successfully.")
        print(f"Workspace: {allowed_folder}")

        print("\nAvailable workflows:")
        print("1. Organize files")
        print("2. Archive old files")
        print("3. Detect duplicate files")
        print("4. Run due scheduled workflows")

        choice = input("Choose a workflow (1, 2, 3, or 4): ").strip()

        if choice == "1":
            workflow_name = "organize"

        elif choice == "2":
            workflow_name = "archive"

            days_input = input(
                "Archive files older than how many days? "
            ).strip()

            try:
                days_old = int(days_input)

                if days_old < 1:
                    raise ValueError

            except ValueError:
                print("Please enter a positive whole number.")
                return

        elif choice == "3":
            workflow_name = "duplicates"

        elif choice == "4":
            run_due_schedules(allowed_folder=allowed_folder)
            return

        else:
            print("Invalid choice.")
            return

        if workflow_name == "archive":
            actions = run_workflow(
                workflow_name, allowed_folder, days_old
            )
        else:
            actions = run_workflow(
                workflow_name, allowed_folder
            )

        if workflow_name == "duplicates":
            if not actions:
                print("No duplicates found.")

            for pair in actions:
                print(f"Original: {pair['original']}")
                print(f"Duplicate: {pair['duplicate']}")

            return

        execute_approved_actions(actions, allowed_folder)

    except (ValueError, OSError, RuntimeError, OverflowError) as error:
        print(f"ERROR: {error}")

    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled.")


if __name__ == "__main__":
    main()