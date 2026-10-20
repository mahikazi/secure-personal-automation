from pathlib import Path
from security.permissions import is_action_allowed
from security.audit_logger import log_action

def execute_action(action, allowed_folder):
    if not is_action_allowed(action, allowed_folder):
        print("BLOCKED: Action is not permitted.")
        log_action(action, "BLOCKED")
        return False

    source = Path(action["source"])
    destination = Path(action["destination"])

    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        destination.hardlink_to(source)
    except FileExistsError:
        print("BLOCKED: Destination already exists.")
        log_action(action, "BLOCKED")
        return False
    source.unlink()

    print(f"MOVED: {source} -> {destination}")
    log_action(action, "SUCCESS")
    return True