# Secure Personal Automation Platform

A Python-based personal automation system designed with cybersecurity principles.

## Features

- Organizes files by extension
- Checks permissions before executing file operations
- Blocks unauthorized file moves
- Prevents overwriting existing destination files
- Records successful and blocked actions in an audit log
- Includes automated security tests

## How to Run

Activate the Python virtual environment, then run:

```bash
python main.py
```

## Security Design

The system separates file organization, permission checking, and execution into independent components.

Actions must pass a permission check before execution.

The permission system also checks for direct source-file symbolic links before resolving file paths.

## Version 0.2 — Security Testing

Version 0.2 introduces automated security testing using Python's built-in unittest framework.

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

## Current Limitations

This is an early prototype, not a fully hardened filesystem sandbox.

Future work includes stronger protection against symlink attacks, filesystem race conditions, execution-time failures, and logging failures.

Future versions will also introduce additional automation workflows, configurable security policies, and a user interface.