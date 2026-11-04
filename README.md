# Secure Personal Automation Platform

A Python-based personal automation system designed with cybersecurity principles.

## Features

### Automation Workflows

- **File Organizer:** Organizes files into folders based on their extensions.
- **Old-File Archiver:** Moves files older than a user-selected number of days into an archive folder.
- **Duplicate Detector:** Uses SHA-256 hashing to identify files with matching contents without moving or deleting them.

### Security Features

- Checks permissions before executing file operations
- Blocks unauthorized file moves
- Prevents overwriting existing destination files
- Records successful and blocked file operations in an audit log
- Attempts to record general filesystem execution failures
- Checks for direct source-file symbolic links before resolving paths
- Validates resolved source and destination paths against an authorized directory
- Supports configurable file-extension and file-size restrictions
- Validates configuration settings before using them
- Uses a custom exception for file-operation failures
- Handles missing files, permission errors, and destination-folder creation failures
- Includes automated permission and executor security tests

## How to Run

Activate the Python virtual environment, then run:

```bash
python3 main.py
```

The program displays a menu with three options:

1. Organize files
2. Archive old files
3. Detect duplicate files

The file organizer sorts files by extension.

The archiver asks the user to enter a file-age threshold in days before identifying files to archive.

The duplicate detector compares SHA-256 hashes and reports files with matching contents. It does not automatically delete or move duplicate files.

## Security Design

The system separates automation workflows, permission checking, configuration management, file execution, and audit logging into independent components.

The workflow manager selects which automation to run.

File-moving actions must pass a permission check before execution.

The permission system checks whether source and destination paths resolve within an authorized directory, prevents overwriting existing destination files, and checks for direct source-file symbolic links before resolving paths.

The permission checker also uses security settings loaded from a JSON configuration file to restrict file extensions and maximum file sizes.

The configured allowed folder is used when no folder is explicitly supplied to the permission checker. Existing callers can still supply an allowed folder directly.

The executor performs an additional permission check after creating the destination directory and before creating the hard link.

File operations use hard-link creation followed by source deletion. This avoids directly overwriting an existing destination but does not provide a fully atomic move.

The duplicate detector is read-only and does not send its results to the file-moving executor.

## Version 0.2 — Security Testing

Version 0.2 introduced automated security testing using Python's built-in `unittest` framework.

The original six security tests cover:

- Authorized file operations
- Unauthorized destination paths
- Overwrite prevention
- Path traversal attempts
- Symbolic links in destination paths
- Symbolic links used as source files

### Running Security Tests

Run the following command from the project directory:

```bash
python3 -m unittest discover -s tests -v
```

## Version 0.3 — Multiple Automation Workflows

Version 0.3 expanded the platform from a basic file organizer into a system supporting three automation workflows.

### File Organizer

Organizes files into folders according to their file extensions.

### Old-File Archiver

Identifies files based on their last modification date and proposes moving older files into an archive folder.

Users can choose how many days old a file must be before it is archived.

Proposed moves are processed through the platform's existing permission checks and execution system.

### Duplicate File Detector

Calculates SHA-256 hashes to identify files with matching contents.

Reports the original and duplicate file paths without automatically deleting, overwriting, or moving any files.

### Workflow Manager

A centralized workflow manager connects the three automation modules to a command-line selection menu.

This allows users to choose which automation to run without modifying the source code.

## Version 0.4 — Configurable Security Policies

Version 0.4 introduced configurable security settings that allow file-operation restrictions to be adjusted without directly modifying the permission-checking code.

### Configuration File

Security settings are stored in `config/settings.json`.

The current configuration is:

```json
{
  "allowed_folder": "test_files",
  "allowed_extensions": [".txt", ".pdf", ".jpg", ".png", ".csv"],
  "max_file_size_mb": 20
}
```

These settings define:

- **Allowed folder:** The directory intended for authorized file operations.
- **Allowed extensions:** The file extensions permitted for file-moving operations.
- **Maximum file size:** The largest permitted source file size, measured in megabytes.

### Configuration Loader

The `config/config_loader.py` module reads the JSON configuration file and converts its contents into a Python dictionary.

The loader validates required configuration values before returning them.

Validation checks include:

- Confirming that the configuration is a JSON object
- Requiring a non-empty allowed-folder string
- Requiring a non-empty list of file extensions
- Checking that each extension begins with a period
- Requiring a positive numeric maximum file size

The loader also reports errors when the configuration file is missing or contains invalid JSON.

### Permission Enforcement

The permission checker enforces additional restrictions:

- Blocks source files whose extensions are not on the configured allowlist
- Blocks source files exceeding the configured maximum file size
- Continues checking authorized paths, symbolic links, and existing destinations

The allowed-folder configuration is used when the permission checker is called without an explicit allowed-folder argument.

### Security Testing

Version 0.4 added tests for:

- Blocking file operations involving disallowed extensions
- Blocking file operations involving files larger than the configured limit

These tests extended the original six-test suite to eight permission tests.

### Configuration Limitations

The current configuration system provides basic security controls but is not a complete policy-enforcement framework.

File-extension restrictions check filenames rather than actual file contents.

File-size and filesystem checks may become outdated if a file changes between validation and execution.

An explicitly supplied allowed-folder argument can still override the configured folder, and the application has not yet been fully updated to enforce the configured folder consistently across every workflow.

## Version 0.5 — Safer File Execution

Version 0.5 improves the file executor's error handling and introduces tests for filesystem failures and partial file operations.

### Custom File-Operation Exception

The `security/exceptions.py` module defines `FileOperationError`, a custom exception used to report failures during file execution.

This allows filesystem errors to be reported through a consistent application-specific exception type.

### Structured Error Handling

The executor uses `try` and `except` blocks to handle filesystem failures.

The updated executor includes handling for:

- Missing source files or required paths
- Permission-denied errors
- Existing destination files
- Destination-folder creation failures
- General operating-system filesystem errors

Destination-folder creation failures are reported with a specific error message.

Existing destination files remain blocked rather than overwritten.

### Additional Permission Validation

The executor performs an additional permission check after attempting to create the destination directory and before creating the destination hard link.

This can detect some changes between the initial permission check and execution.

However, the additional check does not eliminate time-of-check-to-time-of-use (TOCTOU) race conditions.

### Failed-Action Audit Logging

The executor attempts to record a `FAILED` audit event when a general filesystem error occurs.

If writing that failure record raises an `OSError`, the executor prints a warning and continues raising the original filesystem failure as `FileOperationError`.

Successful and blocked operations continue using the existing audit logging system.

Failure logging is not yet consistent across every exception handler, including missing-file errors, permission-denied errors, and destination-folder creation failures.

### Executor Failure Tests

Version 0.5 introduces `tests/test_executor.py`.

The new tests simulate:

- A filesystem error during hard-link creation
- A permission error when deleting the source file after creating the destination hard link

The tests use temporary directories and Python's `unittest.mock` module to simulate failures without intentionally modifying important user files.

The source-deletion failure test demonstrates a known partial-move condition: both source and destination paths may remain after the operation fails.

With the original eight permission tests and two new executor tests, the suite contains ten tests when all tests are present.

Run the complete suite with:

```bash
python3 -m unittest discover -s tests -v
```

### Remaining Execution Limitations

Version 0.5 improves error reporting but does not make file operations fully atomic or guarantee recovery from partial moves.

Known limitations include:

- A failure after hard-link creation may leave both source and destination paths present
- Cross-filesystem moves are not supported by the hard-link approach
- Filesystem paths may change between permission validation and execution
- Some exception handlers do not yet record `FAILED` audit events
- Audit logging failures are not handled consistently across every logging call
- Unexpected execution exceptions may still propagate to callers without a user-friendly message

These limitations require additional security review and testing before production use.

## Current Limitations

SecureFlow remains a cybersecurity-focused prototype, not a fully hardened filesystem sandbox.

Current limitations include:

- Advanced symbolic-link attacks and filesystem race conditions
- Partial file operations without automatic rollback
- Incomplete failure-audit coverage
- Audit logging failures outside the general filesystem-error handler
- Cross-filesystem move restrictions
- Explicit allowed-folder overrides that can bypass the configured folder restriction
- File-extension checks that do not inspect actual file contents
- File-size checks that may become outdated before execution
- Duplicate detection currently examines only the top level of the selected folder
- Matching SHA-256 hashes are not yet verified with a byte-for-byte comparison
- Automation workflows are currently operated through a command-line interface
- Limited integration and adversarial security testing

## Future Development

Planned development milestones include:

- **v0.6 — Workflow Preview and Approval:** Display proposed file changes and require user approval before execution.
- **v0.7 — Scheduling and Automation:** Support configurable schedules and safer unattended workflow execution.
- **v0.8 — Dashboard and Monitoring:** Build a graphical Python dashboard for managing workflows, reviewing previews, approving actions, and viewing audit activity.
- **v0.9 — Integration and Security Review:** Test workflows together, investigate security edge cases, and address remaining implementation weaknesses.
- **v1.0 — Final Release and Demo:** Finalize documentation, installation instructions, demonstrations, and release testing.

The long-term goal is a practical personal automation platform that combines useful workflows with transparent security controls, clear audit records, and predictable failure handling.