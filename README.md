
# Secure Personal Automation Platform

A Python-based personal automation system designed with cybersecurity principles.

## Features

- Organizes files by extension
- Checks permissions before executing file operations
- Blocks unauthorized file moves
- Prevents overwriting existing destination files
- Records successful and blocked actions in an audit log

## How to Run

Activate the Python virtual environment, then run:

```bash
python main.py
```

## Security Design

The system separates file organization, permission checking, and execution into independent components.

Actions must pass a permission check before execution.

## Current Limitations

This is an early prototype, not a fully hardened filesystem sandbox. Future work includes stronger protection against symlink attacks, filesystem race conditions, and logging failures.
