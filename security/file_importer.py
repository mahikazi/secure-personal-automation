import os
import stat
import tempfile
from pathlib import Path

from config.config_loader import load_config
from security.audit_logger import log_action


def import_files(file_paths):
    settings = load_config()

    workspace = Path(
        settings["allowed_folder"]
    ).resolve()

    if not workspace.is_dir():
        raise ValueError("Workspace does not exist.")

    allowed_extensions = settings["allowed_extensions"]
    max_bytes = settings["max_file_size_mb"] * 1024 * 1024

    results = []

    for file_path in file_paths:
        source = Path(file_path)
        destination = workspace / source.name

        status = "FAILED"
        message = ""
        temporary_path = None

        try:
            if source.is_symlink():
                raise ValueError("Symbolic links are not allowed.")

            if not source.is_file():
                raise ValueError("Source must be a regular file.")

            if source.suffix.lower() not in allowed_extensions:
                raise ValueError("File extension is not permitted.")

            if source.stat().st_size > max_bytes:
                raise ValueError("File exceeds the size limit.")

            if destination.exists() or destination.is_symlink():
                raise ValueError("A file with this name already exists.")

            flags = (
                os.O_RDONLY
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_NONBLOCK", 0)
                | getattr(os, "O_BINARY", 0)
            )

            descriptor = os.open(source, flags)

            with os.fdopen(descriptor, "rb") as input_file:
                if not stat.S_ISREG(
                    os.fstat(input_file.fileno()).st_mode
                ):
                    raise ValueError("Source must be a regular file.")

                with tempfile.NamedTemporaryFile(
                    mode="wb",
                    dir=workspace,
                    prefix=".import_",
                    suffix=".tmp",
                    delete=False
                ) as output_file:

                    temporary_path = Path(output_file.name)
                    total_bytes = 0

                    while True:
                        chunk = input_file.read(1024 * 1024)

                        if not chunk:
                            break

                        total_bytes += len(chunk)

                        if total_bytes > max_bytes:
                            raise ValueError(
                                "File exceeds the size limit."
                            )

                        output_file.write(chunk)

                    output_file.flush()
                    os.fsync(output_file.fileno())

            destination.hardlink_to(temporary_path)

            status = "SUCCESS"
            message = "File imported successfully."

        except ValueError as error:
            status = "BLOCKED"
            message = str(error)

        except FileExistsError:
            status = "BLOCKED"
            message = "A file with this name already exists."

        except OSError as error:
            status = "FAILED"
            message = str(error)

        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError as error:
                    message += f" Temporary file cleanup failed: {error}"

        try:
            log_action(
                {
                    "source": f"IMPORT: {source}",
                    "destination": str(destination)
                },
                status
            )

        except OSError:
            message += " Audit logging failed."

        results.append({
            "filename": source.name,
            "source": str(source),
            "destination": str(destination),
            "status": status,
            "message": message
        })

    return results