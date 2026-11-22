from scheduler.scheduled_runner import run_due_schedules
from workflows.workflow_manager import run_workflow
from security.approval_executor import execute_approved_actions

def main():
    print("Secure Personal Automation Platform")
    print("System initialized successfully.")

    print("Available workflows:")
    print("1. Organize files")
    print("2. Archive old files")
    print("3. Detect duplicate files")
    print("4. Run due scheduled workflows")

    choice = input("Choose a workflow (1, 2, 3, or 4): ")

    if choice == "1":
        workflow_name = "organize"

    elif choice == "2":
        workflow_name = "archive"

        days_input = input("Archive files older than how many days? ")

        if not days_input.isdigit() or int(days_input) < 1:
            print("Please enter a positive whole number.")
            return
        
        days_old = int(days_input)

    elif choice == "3":
        workflow_name = "duplicates"

    elif choice == "4":
        run_due_schedules()
        return

    else:
        print("Invalid choice")
        return

    if workflow_name == "archive":
        actions = run_workflow(workflow_name, "test_files", days_old)
    else:
        actions = run_workflow(workflow_name, "test_files")

    if workflow_name == "duplicates":
        if not actions:
            print("No duplicates found.")

        for pair in actions:
            print(f"Original: {pair['original']}")
            print(f"Duplicates: {pair['duplicate']}")

        return

    execute_approved_actions(actions, "test_files")

if __name__ == "__main__":
    main()