from workflows.file_organizer import organize_files
from security.permissions import is_action_allowed
from security.executor import execute_action

def main():
    print("Secure Personal Automation Platform")
    print("System initialized successfully.")

    actions = organize_files("test_files")

    for action in actions:
        print(f"Proposed move: {action['source']} -> {action['destination']}")
        allowed = is_action_allowed(action, "test_files")
        print(f"Permission granted: {allowed}")
        if allowed:
            execute_action(action, "test_files")

if __name__ == "__main__":
    main()