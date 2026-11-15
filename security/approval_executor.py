from security.preview import preview_actions
from security.approval import request_approval
from security.executor import execute_action
from security.audit_logger import log_action
from security.exceptions import FileOperationError

def record_action_status(action, status):
    try:
        log_action(action, status)
    except OSError as log_error:
        print(f"WARNING: Could not write audit log: {log_error}")

def execute_approved_actions(actions, allowed_folder):
    if not actions:
        print("No proposed file actions.")
        return 0

    allowed_actions, blocked_actions = preview_actions(
        actions,
        allowed_folder
    )

    for action in blocked_actions:
        record_action_status(action, "BLOCKED")

    if not allowed_actions:
        print("No permitted actions to execute.")
        return 0

    approved = request_approval(len(allowed_actions))

    if not approved:
        print("Workflow cancelled. No files were moved.")

        for action in allowed_actions:
            record_action_status(action, "CANCELLED")

        return 0

    successful_actions = 0

    for action in allowed_actions:
        try:
            if execute_action(action, allowed_folder):
                successful_actions +=1

        except FileOperationError as error:
            print(f"ERROR: {error}")

    print("\n=== EXECUTION SUMMARY ===")
    print(f"Approved actions: {len(allowed_actions)}")
    print(f"Successful actions: {successful_actions}")
    print(
        f"Unsuccessful actions: "
        f"{len(allowed_actions) - successful_actions}"
    )

    return successful_actions