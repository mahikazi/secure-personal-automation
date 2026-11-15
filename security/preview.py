from pathlib import Path
from security.permissions import is_action_allowed

def preview_action(action, allowed_folder):
    source = Path(action["source"])
    destination = Path(action["destination"])

    allowed = is_action_allowed(action, allowed_folder)

    print(f"Source:      {source}")
    print(f"Destination: {destination}")

    if allowed:
        print("Status:      ALLOWED")
    else:
        print("Status:      BLOCKED")

    print("-" * 50)

    return allowed

def preview_actions(actions, allowed_folder):
    print("\n=== WORKFLOW PREVIEW ===")
    print(f"Total proposed actions: {len(actions)}")
    print("-" * 50)

    allowed_actions = []
    blocked_actions = []

    for number, action in enumerate(actions, start=1):
        print(f"\nAction {number}")

        if preview_action(action, allowed_folder):
            allowed_actions.append(action)
        else:
            blocked_actions.append(action)

    print("\n=== PREVIEW SUMMARY ===")
    print(f"Allowed actions: {len(allowed_actions)}")
    print(f"Blocked actions: {len(blocked_actions)}")

    return allowed_actions, blocked_actions