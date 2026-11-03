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

The system separates automation workflows, permission checking, and file execution into independent components.

The workflow manager selects which automation to run.

File-moving actions must pass a permission check before execution.

The permission system restricts file operations to an authorized directory, prevents overwriting existing destination files, and checks for direct source-file symbolic links before resolving paths.

The duplicate detector is read-only and does not send its results to the file-moving executor.

## Version 0.2 — Security Testing

Version 0.2 introduced automated security testing using Python's built-in `unittest` framework.

The six security tests cover:

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

## Current Limitations

This is an early prototype, not a fully hardened filesystem sandbox.

Current limitations include:

- More complex symbolic-link attacks
- Filesystem race conditions between permission checks and execution
- Execution-time failures and partial file operations
- Audit logging failures
- Duplicate detection currently examines only the top level of the selected folder
- Matching SHA-256 hashes are not yet verified with a byte-for-byte comparison
- Automation workflows are currently operated through a command-line interface

## Future Development

Future versions will focus on:

- Stronger security controls and safer file execution
- Configurable security policies
- Scheduled automation workflows
- Expanded automation capabilities
- A graphical dashboard for managing workflows and viewing activity logs