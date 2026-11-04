import errno

from pathlib import Path
from security.permissions import is_action_allowed
from security.audit_logger import log_action
from security.exceptions import FileOperationError

def execute_action(action, allowed_folder):
    if not is_action_allowed(action, allowed_folder):
        print("BLOCKED: Action is not permitted.")

        try:
            log_action(action, "BLOCKED")
        except OSError as log_error:
            print(f"WARNING: Could not write audit log: {log_error}")
        
        return False

    source = Path(action["source"])
    destination = Path(action["destination"])

    try:
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)

        except OSError as error:
            try:
                log_action(action, "FAILED")
            except OSError as log_error:
                print(f"WARNING: Could not write audit log: {log_error}")

            raise FileOperationError(
                f"Could not create destination folder: {error}"
            ) from error

        if not is_action_allowed(action, allowed_folder):
            try:
                log_action(action, "BLOCKED")
            except OSError as log_error:
                print(f"WARNING: Could not write audit log: {log_error}")
        
            return False
        
        destination.hardlink_to(source)
        source.unlink()

    except FileExistsError:
        print(f"BLOCKED: Destination already exists: {destination}")

        try:
            log_action(action, "BLOCKED")
        except OSError as log_error:
            print(f"WARNING: Could not write audit log: {log_error}")
        
        return False

    except FileNotFoundError as error:
        try:
            log_action(action, "FAILED")
        except OSError as log_error:
            print(f"WARNING: Could not write audit log: {log_error}")
        
        raise FileOperationError(
            f"Source file or required path is missing: {error}"
        ) from error

    except PermissionError as error:
        try:
            log_action(action, "FAILED")
        except OSError as log_error:
            print(f"WARNING: Could not write audit log: {log_error}")

        raise FileOperationError(
            f"Permission denied during file operation: {error}"
        ) from error

    except OSError as error:
        try:
            log_action(action, "FAILED")
        except OSError as log_error:
            print(f"WARNING: Could not write audit log: {log_error}")

        if error.errno == errno.EXDEV:
            raise FileOperationError(
                "Cross-filesystem moves are not supported."
            ) from error

        raise FileOperationError(
            f"File operation failed: {error}"
        ) from error

    print(f"MOVED: {source} -> {destination}")

    try:
        log_action(action, "SUCCESS")
    except OSError as log_error:
        print(f"WARNING: Move succeeded, but audit logging failed: {log_error}")
    
    return True