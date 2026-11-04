# Secure Personal Automation Platform

A Python-based personal automation system designed with cybersecurity principles.

SecureFlow combines useful file automation workflows with permission validation, configurable security policies, filesystem error handling, and audit logging.

## Features

### Automation Workflows

- **File Organizer:** Organizes files into folders based on their extensions.
- **Old-File Archiver:** Moves files older than a user-selected number of days into an archive folder.
- **Duplicate Detector:** Uses SHA-256 hashing to identify files with matching contents without moving or deleting them.

### Security Features

- Validates permissions before executing file operations
- Blocks unauthorized file moves and path traversal attempts
- Prevents overwriting existing destination files
- Rejects direct symbolic-link sources and symbolic-link destinations
- Validates resolved paths against an authorized directory
- Enforces configurable file-extension and file-size restrictions
- Validates JSON configuration settings
- Rechecks permissions immediately before file execution
- Uses a custom exception for filesystem operation failures
- Handles missing files, permission errors, and destination-folder creation failures
- Detects and reports unsupported cross-filesystem moves
- Attempts to audit successful, blocked, and failed file operations
- Handles audit-log write failures without hiding the original filesystem error
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

The executor performs an additional permission check after creating the destination directory and before creating the destination hard link.

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

The configuration system provides basic security controls but is not a complete policy-enforcement framework.

File-extension restrictions check filenames rather than actual file contents.

File-size and filesystem checks may become outdated if a file changes between validation and execution.

An explicitly supplied allowed-folder argument can still override the configured folder, and the application does not yet consistently enforce the configured folder across every workflow.

## Version 0.5 — Safer File Execution

Version 0.5 provides structured filesystem error handling, additional permission validation, improved audit logging, and automated tests for execution failures.

### Custom File-Operation Exception

The `security/exceptions.py` module defines `FileOperationError`, a custom exception used to report failures during file execution.

This provides a consistent application-specific exception type for supported filesystem failures.

### Structured Error Handling

The executor uses `try` and `except` blocks to handle filesystem failures.

Supported error handling includes:

- **Missing files:** Reports missing source files or required filesystem paths.
- **Permission-denied errors:** Reports filesystem permission failures.
- **Existing destinations:** Blocks operations that would overwrite an existing destination.
- **Destination-folder creation failures:** Reports errors encountered while preparing destination directories.
- **General filesystem errors:** Converts operating-system errors into `FileOperationError`.
- **Cross-filesystem moves:** Detects `errno.EXDEV` and reports that cross-filesystem moves are unsupported.

Existing destination files are blocked rather than overwritten.

### Additional Permission Validation

The executor performs two permission checks:

1. Before beginning the file operation.
2. After creating the destination directory and before creating the destination hard link.

The second check can detect some changes to file paths or permissions between initial validation and execution.

However, repeated validation does not eliminate time-of-check-to-time-of-use (TOCTOU) race conditions.

### Hard-Link-Based File Execution

File moves use the following sequence:

1. Validate the requested action.
2. Prepare the destination directory.
3. Revalidate the requested action.
4. Create a hard link at the destination.
5. Delete the original source path.
6. Record the operation result in the audit log.

Hard-link creation avoids directly overwriting an existing destination.

However, the overall move is not atomic.

If source deletion fails after hard-link creation, both source and destination paths may remain.

The executor does not automatically roll back these partial operations.

Hard links also cannot be created across different filesystems, so cross-filesystem moves are explicitly unsupported.

### Audit Logging

The executor records operation outcomes using the audit logger in `security/audit_logger.py`.

Audit statuses include:

- **SUCCESS:** The file operation completed.
- **BLOCKED:** The requested action was rejected.
- **FAILED:** A supported filesystem error prevented completion.

The executor attempts to record `FAILED` events for:

- Missing-file errors
- Permission-denied errors
- Destination-folder creation failures
- General filesystem errors, including unsupported cross-filesystem moves

Blocked actions are also logged, including actions rejected during permission validation and attempts to use an existing destination.

### Audit Logging Error Handling

Audit logging is handled separately from the underlying filesystem operation.

If writing a `FAILED` event raises an `OSError`, the executor prints a warning and preserves the original filesystem failure as `FileOperationError`.

If writing a `BLOCKED` event raises an `OSError`, the executor prints a warning and still returns `False`.

If a move succeeds but writing its `SUCCESS` event fails, the executor prints a warning and still returns `True`.

This distinction prevents an audit-log write failure from incorrectly changing the reported outcome of the file operation.

**Security limitation:** Audit records are best-effort. A file operation may complete or be blocked without a successfully written audit record. The current implementation does not provide guaranteed or tamper-resistant audit logging.

### Executor Security Tests

Version 0.5 includes `tests/test_executor.py`.

The executor tests cover:

1. **Filesystem failure:** Simulates a disk error during hard-link creation and verifies that `FileOperationError` is raised.
2. **Source deletion failure:** Simulates a permission error when deleting the original source after hard-link creation and verifies that both paths remain.
3. **Audit logging failure:** Simulates simultaneous filesystem and audit-log errors and verifies that the original filesystem error is preserved.

The tests use temporary directories and Python's `unittest.mock` module to simulate failures without intentionally modifying important user files.

### Complete Test Suite

The test suite contains:

| Test category | Number of tests |
|---|---:|
| Permission security tests | 8 |
| Executor failure tests | 3 |
| **Total** | **11** |

Run the complete suite from the project directory:

```bash
python3 -m unittest discover -s tests -v
```

The expected successful result is:

```text
Ran 11 tests

OK
```

### Remaining Execution Limitations

Version 0.5 improves file-execution security and error handling but does not make file operations fully atomic or guarantee recovery from partial moves.

Known limitations include:

- A failure after hard-link creation may leave both source and destination paths present.
- Automatic rollback of partial moves is not implemented.
- Cross-filesystem moves are not supported.
- Filesystem paths may change between permission validation and execution.
- Repeated permission checks do not eliminate TOCTOU vulnerabilities.
- Audit logging is best-effort and may fail without preventing an operation.
- Audit records are not tamper-resistant.
- Unexpected exceptions outside the supported filesystem error handlers may still propagate to callers.
- File operations do not yet require interactive preview and approval.

These limitations require additional security review and testing before production use.

## Current Limitations

SecureFlow remains a cybersecurity-focused prototype, not a fully hardened filesystem sandbox.

Current limitations include:

- Advanced symbolic-link attacks and filesystem race conditions
- Partial file operations without automatic rollback
- Best-effort rather than guaranteed audit logging
- Cross-filesystem move restrictions
- Explicit allowed-folder overrides that can bypass the configured folder restriction
- File-extension checks that do not inspect actual file contents
- File-size checks that may become outdated before execution
- Duplicate detection currently examines only the top level of the selected folder
- Matching SHA-256 hashes are not yet verified with a byte-for-byte comparison
- Automation workflows are currently operated through a command-line interface
- No interactive preview or approval stage before file execution
- No scheduling or graphical dashboard
- Limited integration and adversarial security testing

## Future Development

Planned development milestones include:

- **v0.6 — Workflow Preview and Approval:** Display proposed file changes and require user approval before execution.
- **v0.7 — Scheduling and Automation:** Support configurable schedules and safer unattended workflow execution.
- **v0.8 — Dashboard and Monitoring:** Build a graphical Python dashboard for managing workflows, reviewing previews, approving actions, and viewing audit activity.
- **v0.9 — Integration and Security Review:** Test workflows together, investigate security edge cases, and address remaining implementation weaknesses.
- **v1.0 — Final Release and Demo:** Finalize documentation, installation instructions, demonstrations, and release testing.

The long-term goal is a practical personal automation platform that combines useful workflows with transparent security controls, clear audit records, and predictable failure handling.