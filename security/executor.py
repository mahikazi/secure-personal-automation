import errno

from pathlib import Path
from security.permissions import is_action_allowed
from security.audit_logger import log_action
from security.exceptions import FileOperationError


def record_status(action, status):
    try:
        log_action(action, status)
    except OSError as error:
        print(f"WARNING: Could not write audit log: {error}")


def execute_action(action, allowed_folder):
    if not is_action_allowed(action, allowed_folder):
        print("BLOCKED: Action is not permitted.")
        record_status(action, "BLOCKED")
        return False

    source = Path(action["source"])
    destination = Path(action["destination"])

    try:
        destination.parent.mkdir(parents=True, exist_ok=True)

        if not is_action_allowed(action, allowed_folder):
            record_status(action, "BLOCKED")
            return False

        destination.hardlink_to(source)

    except FileExistsError:
        print(f"BLOCKED: Destination already exists: {destination}")
        record_status(action, "BLOCKED")
        return False

    except FileNotFoundError as error:
        record_status(action, "FAILED")

        raise FileOperationError(
            f"Source file or required path is missing: {error}"
        ) from error

    except PermissionError as error:
        record_status(action, "FAILED")

        raise FileOperationError(
            f"Permission denied during file operation: {error}"
        ) from error

    except OSError as error:
        record_status(action, "FAILED")

        if error.errno == errno.EXDEV:
            raise FileOperationError(
                "Cross-filesystem moves are not supported."
            ) from error

        raise FileOperationError(
            f"File operation failed: {error}"
        ) from error

    try:
        source.unlink()

    except OSError as error:
        record_status(action, "FAILED")

        raise FileOperationError(
            f"Destination link created, but source removal failed. "
            f"Both paths may remain: {source} and {destination}. "
            f"Original error: {error}"
        ) from error

    print(f"MOVED: {source} -> {destination}")
    record_status(action, "SUCCESS")

    return True