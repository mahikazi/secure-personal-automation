
# SecureFlow — Secure Personal Automation

SecureFlow is a Python-based file automation project built with a focus on cybersecurity and controlled file operations.

The goal is to automate common file management tasks without giving the program unrestricted access to the filesystem. Instead of moving files immediately, SecureFlow checks whether each action is allowed, displays the proposed changes, and asks for approval before executing them.

The project currently supports file organization, old-file archiving, duplicate detection, and interval-based workflow scheduling.

**Current Version:** v0.7 — Scheduling and Automation

## Features

### File Organization

The file organizer sorts files into folders based on their extensions.

For example, a `.txt` file can be moved into a `txt` folder inside the authorized directory.

Before moving anything, SecureFlow checks the proposed source and destination paths against its security rules. Permitted actions are shown in a preview and require user approval.

### File Archiving

The archiver identifies files that have not been modified within a specified number of days.

Users can enter an age threshold through the command-line menu, and SecureFlow generates proposed moves into an archive folder.

Existing destination files are protected from being overwritten, and only approved actions are executed.

### Duplicate Detection

The duplicate detector uses SHA-256 hashing to identify files with matching contents.

It reports the original and duplicate file paths without deleting, overwriting, or moving either file.

This workflow is read-only and does not require file-move approval.

### Workflow Preview and Approval

Before executing file-moving workflows, SecureFlow displays:

- The source file path
- The proposed destination path
- Whether the action is `ALLOWED` or `BLOCKED`
- The total number of permitted and blocked actions

Only permitted actions can be approved. Blocked actions are excluded from execution.

Users can enter `y` or `yes` to approve a workflow, or `n` or `no` to cancel it.

If approval is declined, the proposed file moves are not executed.

### Workflow Scheduling

Version 0.7 introduced configurable scheduling for the organizer, archiver, and duplicate detector.

Schedules are defined in a JSON file and use time intervals to determine when workflows should run.

SecureFlow records the last time each schedule was processed so it does not run again before its configured interval has passed.

Scheduling is currently triggered through the command-line menu rather than running continuously in the background.

Scheduled file-moving workflows still go through the same security checks, preview, and approval process.

## Getting Started

### Requirements

- Python 3
- Git
- macOS, Linux, or Windows with a compatible Python environment

The project uses Python's standard library and does not currently require third-party Python packages.

### Installation

Clone the repository:

```bash
git clone https://github.com/mahikazi/secure-personal-automation.git
cd secure-personal-automation
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Run the application:

```bash
python3 main.py
```

### Command-Line Menu

When the program starts, it displays:

```text
Secure Personal Automation Platform
System initialized successfully.

Available workflows:
1. Organize files
2. Archive old files
3. Detect duplicate files
4. Run due scheduled workflows
```

Select a workflow by entering its corresponding number.

For file-moving workflows, SecureFlow displays the proposed actions before asking for approval.

## Security Design

Security checks are separated from the automation logic so workflows cannot directly execute file moves without passing through the permission and execution components.

### Permission Validation

The permission checker in `security/permissions.py` evaluates file operations before they are executed.

It checks that:

- Source and destination paths resolve inside the authorized directory.
- The source exists and is a regular file.
- Direct symbolic-link sources are rejected.
- Symbolic-link destinations are rejected.
- Existing destination files are not overwritten.
- The source file extension is permitted.
- The source file size does not exceed the configured limit.

These checks help prevent unauthorized file operations, path traversal, and accidental overwriting.

### File Execution

File operations are handled by `security/executor.py`.

The executor performs an additional permission check before modifying files.

File moves use hard-link creation followed by deletion of the original source path. This avoids directly overwriting an existing destination.

The executor also handles common filesystem errors, including missing files, permission failures, and unsupported cross-filesystem moves.

These operations are not fully atomic, and some filesystem race conditions remain possible.

### Audit Logging

SecureFlow uses `security/audit_logger.py` to record file-operation outcomes.

Recorded statuses include:

| Status | Meaning |
|--------|---------|
| `SUCCESS` | File operation completed |
| `BLOCKED` | Action failed a security check |
| `FAILED` | File operation encountered an error |
| `CANCELLED` | User declined approval |

Audit logging is best-effort. If writing to the log fails, SecureFlow reports a warning without replacing the original file-operation result.

## Configuration

### Security Settings

Security settings are stored in `config/settings.json`.

```json
{
  "allowed_folder": "test_files",
  "allowed_extensions": [".txt", ".pdf", ".jpg", ".png", ".csv"],
  "max_file_size_mb": 20
}
```

The configuration controls which directory can be used for file operations, which file extensions are allowed, and the maximum permitted file size.

The configuration loader validates these settings before they are used.

### Workflow Schedules

Schedules are stored in `config/schedules.json`.

```json
{
  "schedules": [
    {
      "name": "daily_organizer",
      "workflow": "organize",
      "interval_minutes": 1440,
      "enabled": true
    },
    {
      "name": "weekly_archiver",
      "workflow": "archive",
      "interval_minutes": 10080,
      "days_old": 30,
      "enabled": true
    }
  ]
}
```

Each schedule includes a unique name, workflow type, interval, and enabled status.

Archive schedules also require a `days_old` value.

The scheduler validates the configuration and rejects invalid intervals, unsupported workflows, duplicate schedule names, and missing archive settings.

### Scheduling History

The scheduler stores previously processed timestamps in:

`logs/schedule_history.json`

When option `4` is selected, SecureFlow:

1. Loads the configured schedules.
2. Reads the scheduling history.
3. Checks which enabled schedules are due.
4. Processes the due workflows.
5. Updates the scheduling history.

A workflow is recorded as processed even if its file actions are cancelled or blocked. This prevents immediate retries before the next scheduled interval.

If no schedules are due, the program displays:

```text
No scheduled workflows are due.
```

The scheduling history is local runtime data and is excluded from version control.

## Project Structure

The main components are organized as follows:

```text
secure-personal-automation/
├── main.py
├── config/
│   ├── config_loader.py
│   ├── settings.json
│   └── schedules.json
├── workflows/
│   └── workflow_manager.py
├── security/
│   ├── permissions.py
│   ├── executor.py
│   ├── exceptions.py
│   ├── preview.py
│   ├── approval.py
│   ├── approval_executor.py
│   └── audit_logger.py
├── scheduler/
│   ├── schedule_config.py
│   ├── schedule_manager.py
│   ├── schedule_history.py
│   └── scheduled_runner.py
├── tests/
├── test_files/
└── logs/
```

The automation workflows generate proposed file actions, while the security modules handle permission checks, approval, execution, and logging.

The scheduler connects to the existing workflow manager rather than implementing separate file-moving logic.

## Testing

SecureFlow uses Python's built-in `unittest` framework.

Tests cover permission validation, filesystem failures, workflow previews, approval behavior, scheduling configuration, and scheduled workflow execution.

### Test Coverage

| Test Category | Tests |
|---------------|------:|
| Permission security | 8 |
| File execution and error handling | 3 |
| Workflow preview | 3 |
| User approval | 4 |
| Approval and execution | 7 |
| Schedule configuration | 5 |
| Schedule management | 5 |
| Scheduled workflow execution | 4 |
| **Total** | **39** |

Run all tests using:

```bash
python3 -m unittest discover -s tests -v
```

**Latest verified result: 39 tests passed.**

### Manual Testing

The command-line workflows have also been tested manually.

Testing included:

- Approving file moves and verifying successful execution.
- Cancelling workflows and confirming files were not moved.
- Blocking actions with existing destination files.
- Separating permitted and blocked actions in workflow previews.
- Running scheduled organizer and archiver workflows.
- Confirming scheduling history prevents immediate repeated runs.

During the v0.7 scheduler test, two workflows were processed. The organizer was cancelled by the user, and the archiver was blocked because its destination already existed.

Running the scheduler again immediately displayed `No scheduled workflows are due.`, confirming that the history was saved and used correctly.

## Development Progress

| Version | Development |
|---------|-------------|
| v0.1 | Basic file organizer, permission checks, file execution, and audit logging |
| v0.2 | Initial automated security tests |
| v0.3 | File archiving, duplicate detection, and workflow management |
| v0.4 | Configurable security policies |
| v0.5 | Improved file execution and error handling |
| v0.6 | Workflow previews, approval, and cancellation |
| v0.7 | Configurable scheduling and scheduling history |
| v0.8 | Dashboard and monitoring (planned) |
| v0.9 | Integration testing and security review (planned) |
| v1.0 | Final release and demonstration (planned) |

## Current Limitations

SecureFlow is still under development and is not intended to be a fully hardened filesystem security tool.

Current limitations include:

- File operations are not fully atomic, and partial moves are not automatically rolled back.
- Repeated permission checks do not eliminate time-of-check-to-time-of-use (TOCTOU) race conditions.
- Audit logging is best-effort and is not tamper-resistant.
- Cross-filesystem moves are not supported.
- Duplicate detection checks only the top level of the selected directory and does not perform byte-for-byte verification after hashing.
- File-extension checks do not inspect actual file contents.
- Scheduling requires the user to launch the CLI and select option `4`.
- Scheduled file moves still require interactive approval.
- Scheduling history tracks processing times rather than detailed success or failure outcomes.
- A graphical dashboard has not yet been implemented.

## Next Steps

The next development milestone is **v0.8 — Dashboard and Monitoring**.

The plan is to build a Python-based interface for selecting workflows, reviewing proposed file operations, approving actions, and viewing audit activity.

Later versions will focus on integration testing, additional security review, and preparing the project for its final demonstration.