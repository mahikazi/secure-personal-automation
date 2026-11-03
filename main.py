from workflows.workflow_manager import run_workflow
from security.permissions import is_action_allowed
from security.executor import execute_action

def main():
    print("Secure Personal Automation Platform")
    print("System initialized successfully.")

    print("Available workflows:")
    print("1. Organize files")
    print("2. Archive old files")
    print("3. Detect duplicate files")

    choice = input("Choose a workflow (1, 2, or 3): ")

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

    for action in actions:
        print(f"Proposed move: {action['source']} -> {action['destination']}")
        allowed = is_action_allowed(action, "test_files")
        print(f"Permission granted: {allowed}")
        if allowed:
            execute_action(action, "test_files")

if __name__ == "__main__":
    main()