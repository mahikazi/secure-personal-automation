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
- Checks for direct source-file symbolic links before resolving paths
- Supports configurable file-extension and file-size restrictions
- Validates configuration settings before using them
- Includes automated security tests

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

The system separates automation workflows, permission checking, configuration management, and file execution into independent components.

The workflow manager selects which automation to run.

File-moving actions must pass a permission check before execution.

The permission system checks whether source and destination paths are within an authorized directory, prevents overwriting existing destination files, and checks for direct source-file symbolic links before resolving paths.

The permission checker also uses security settings loaded from a JSON configuration file to restrict file extensions and maximum file sizes.

The configured allowed folder is used when no folder is explicitly supplied to the permission checker. Existing callers can still supply an allowed folder directly.

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

Version 0.4 introduces configurable security settings that allow file-operation restrictions to be adjusted without directly modifying the permission-checking code.

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

The permission checker now enforces additional restrictions:

- Blocks source files whose extensions are not on the configured allowlist
- Blocks source files exceeding the configured maximum file size
- Continues checking authorized paths, symbolic links, and existing destinations

The allowed-folder configuration is used when the permission checker is called without an explicit allowed-folder argument.

### Security Testing

Version 0.4 adds tests for:

- Blocking file operations involving disallowed extensions
- Blocking file operations involving files larger than the configured limit

These tests extend the existing security test suite.

### Configuration Limitations

The current configuration system provides basic security controls but is not a complete policy-enforcement framework.

File-extension restrictions check filenames rather than actual file contents.

File-size and filesystem checks may become outdated if a file changes between validation and execution.

An explicitly supplied allowed-folder argument can still override the configured folder, and the application has not yet been fully updated to enforce the configured folder consistently across every workflow.

## Current Limitations

This is an early prototype, not a fully hardened filesystem sandbox.

Current limitations include:

- More complex symbolic-link attacks
- Filesystem race conditions between permission checks and execution
- Execution-time failures and partial file operations
- Audit logging failures
- Explicit allowed-folder overrides that can bypass the configured folder restriction
- File-extension checks that do not inspect actual file contents
- File-size checks that may become outdated before execution
- Duplicate detection currently examines only the top level of the selected folder
- Matching SHA-256 hashes are not yet verified with a byte-for-byte comparison
- Automation workflows are currently operated through a command-line interface

## Future Development

Future versions will focus on:

- Stronger security controls and safer file execution
- Consistent enforcement of configured security policies across workflows
- Workflow previews and user approval before file changes
- Scheduled automation workflows
- Expanded automation capabilities
- A graphical dashboard for managing workflows and viewing activity logs
- Comprehensive integration testing and security review
- Final documentation and a version 1.0 release