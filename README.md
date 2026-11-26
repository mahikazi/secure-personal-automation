# SecureFlow — Secure Personal Automation

SecureFlow is a Python-based file automation platform built with a focus on cybersecurity, filesystem safety, and user control.

I started this project to explore how everyday automation can be implemented without giving a program unrestricted access to the filesystem. Rather than executing file operations immediately, SecureFlow validates proposed actions, previews changes, and requires user approval before moving files.

**Current Version:** v0.9 — Integration Testing and Security Review

## Features

- **File organization:** Sorts files into folders based on their extensions.
- **File archiving:** Identifies and archives files based on their last modified date.
- **Duplicate detection:** Uses SHA-256 hashing to identify duplicate files without modifying or deleting them.
- **Workflow approval:** Previews permitted and blocked actions before execution.
- **Scheduling:** Supports configurable workflow intervals and tracks previous processing times.
- **Audit logging:** Records successful, blocked, failed, and cancelled operations.
- **Graphical dashboard:** Provides an interactive interface for managing workflows and monitoring activity.

## Dashboard

The dashboard is built with CustomTkinter and features a monochromatic dark interface.

It includes five sections:

- **Overview:** Automation activity, pending schedules, and quick actions.
- **Workflows:** Workflow selection, previews, approval, and cancellation.
- **Schedules:** Configured workflows, due status, and scheduling history.
- **Activity:** Searchable audit logs with status filtering.
- **Settings:** Current workspace and security configuration.

Both the dashboard and command-line interface use the same underlying security and automation components.

## Security Design

Security is a central part of SecureFlow rather than an additional feature.

The platform implements:

- Authorized workspace restrictions and path traversal prevention
- Symbolic-link validation
- Configurable file extension and size restrictions
- Destination overwrite prevention
- Permission revalidation before execution
- Explicit user approval for file-moving operations
- Audit log sanitization to prevent newline-based log injection
- Partial-move failure detection and reporting
- Atomic replacement of scheduling history files

File moves use hard-link creation followed by source removal to avoid overwriting existing destination files.

The security layer is separated from workflow generation, allowing automation logic to propose actions without directly executing them.

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core application and automation |
| CustomTkinter | Graphical dashboard |
| Tkinter | GUI components and event handling |
| SHA-256 | Duplicate file detection |
| JSON | Configuration and scheduling history |
| unittest | Automated and integration testing |
| Git & GitHub | Version control |

## Getting Started

### Requirements

- Python 3 with Tkinter support
- Git
- CustomTkinter 6.0.0

Developed and tested on macOS using Python 3.14.6 and Tk 9.0.3.

### Installation

```bash
git clone https://github.com/mahikazi/secure-personal-automation.git
cd secure-personal-automation

python3 -m venv .venv
source .venv/bin/activate

./.venv/bin/python -m pip install -r requirements.txt
```

### Running SecureFlow

Launch the graphical dashboard:

```bash
./.venv/bin/python -m dashboard.app
```

Or use the command-line interface:

```bash
./.venv/bin/python main.py
```

## Configuration

Security policies are defined in `config/settings.json`.

```json
{
  "allowed_folder": "test_files",
  "allowed_extensions": [".txt", ".pdf", ".jpg", ".png", ".csv"],
  "max_file_size_mb": 20
}
```

Workflow schedules are defined in `config/schedules.json`.

```json
{
  "schedules": [
    {
      "name": "daily_organizer",
      "workflow": "organize",
      "interval_minutes": 1440,
      "enabled": true
    }
  ]
}
```

Scheduled workflows are manually triggered and remain subject to permission checks and user approval.

## Project Structure

```text
secure-personal-automation/
├── config/          # Configuration and security policies
├── dashboard/       # Graphical interface
├── scheduler/       # Workflow scheduling and history
├── security/        # Permissions, execution, approval, and logging
├── workflows/       # File automation logic
├── tests/           # Automated and integration tests
├── test_files/      # Authorized testing workspace
├── logs/            # Runtime scheduling data
├── main.py          # Command-line interface
├── requirements.txt
└── README.md
```

## Testing

SecureFlow currently has 73 passing automated tests.

| Test Category | Tests |
|---------------|------:|
| Permission validation | 8 |
| File execution and error handling | 3 |
| Workflow preview | 3 |
| User approval | 4 |
| Approval and execution | 7 |
| Scheduling | 14 |
| Dashboard functionality | 18 |
| Security hardening | 6 |
| Workflow integration | 5 |
| Runtime integrity | 5 |
| **Total** | **73** |

Run the test suite:

```bash
./.venv/bin/python -m unittest discover -s tests -v
```

Manual testing has also been performed to verify dashboard functionality, workflow cancellation, overwrite prevention, symbolic-link protection, file size restrictions, audit log sanitization, and scheduling history integrity.

## Development Progress

| Version | Milestone |
|---------|-----------|
| v0.1 | Core automation and security |
| v0.2 | Automated security testing |
| v0.3 | Workflow expansion |
| v0.4 | Configurable security policies |
| v0.5 | Safer file execution |
| v0.6 | Workflow preview and approval |
| v0.7 | Scheduling and automation |
| v0.8 | Dashboard and monitoring |
| v0.9 | Integration testing and security hardening |
| v1.0 | Final release and demonstration (upcoming) |

## Limitations

SecureFlow is a personal cybersecurity and software development project, not a production-grade filesystem security tool.

- File moves are not fully atomic and remain susceptible to filesystem race conditions.
- Audit logs are not tamper-resistant.
- Cross-filesystem moves are not supported.
- Duplicate detection is limited to the top level of the workspace.
- Scheduling requires manual interaction rather than a background service.
- Dashboard compatibility has primarily been tested on macOS.

## Next Steps

The final development phase will focus on project stabilization, additional regression testing, documentation, and preparing the v1.0 release.