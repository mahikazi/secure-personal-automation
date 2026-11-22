# SecureFlow: Secure Personal Automation

A Python-based personal automation platform designed with cybersecurity principles.

SecureFlow combines practical file automation workflows with permission validation, configurable security policies, workflow previews, explicit user approval, filesystem error handling, audit logging, and configurable workflow scheduling.

**Current version:** v0.7 — Scheduling and Automation

## Features

### Automation Workflows

- **File Organizer:** Organizes files into folders based on their extensions.
- **Old-File Archiver:** Identifies files older than a specified number of days and proposes moving them into an archive folder.
- **Duplicate Detector:** Uses SHA-256 hashing to identify files with matching contents without moving or deleting them.
- **Workflow Scheduler:** Checks configurable schedules and runs workflows when their intervals have elapsed.

### Security Features

- Validates permissions before executing file operations.
- Blocks unauthorized file moves and path traversal attempts.
- Prevents overwriting existing destination files.
- Rejects direct symbolic-link sources and symbolic-link destinations.
- Validates resolved paths against an authorized directory.
- Enforces configurable file-extension and file-size restrictions.
- Validates JSON configuration settings.
- Previews proposed file operations before execution.
- Separates permitted actions from blocked actions.
- Requires explicit user approval before executing permitted file moves.
- Supports cancellation without executing proposed actions.
- Rechecks permissions immediately before file execution.
- Uses a custom exception for filesystem operation failures.
- Handles missing files, permission errors, and destination-folder creation failures.
- Detects and reports unsupported cross-filesystem moves.
- Attempts to audit successful, blocked, failed, and cancelled file operations.
- Handles audit-log write failures without hiding the original filesystem error.
- Validates schedule configurations and prevents premature workflow reruns.
- Stores scheduling history to track previously processed workflows.
- Includes **39 automated security, workflow, and scheduling tests**.

## How to Run

Activate the Python virtual environment, then run:

```bash
python3 main.py
```

The program displays four workflow options:

1. Organize files
2. Archive old files
3. Detect duplicate files
4. Run due scheduled workflows

### File Organizer

The organizer identifies files and proposes sorting them into folders based on their extensions.

Before moving files, SecureFlow displays a preview and requests approval for permitted actions.

### Old-File Archiver

The archiver asks the user to enter a positive whole-number threshold representing how many days old a file must be.

Files older than the threshold are proposed for archiving.

Each proposed move is checked against the security policy before the user is asked to approve permitted actions.

### Duplicate Detector

The duplicate detector calculates SHA-256 hashes and reports files with matching contents.

It is read-only and does not automatically delete, overwrite, or move duplicate files.

Duplicate detection does not require file-move approval because it does not execute file-moving actions.

### Scheduled Workflows

Select option `4` to check whether any configured workflows are due.

SecureFlow reads schedule definitions, checks the last recorded processing time, and processes schedules whose intervals have elapsed.

Supported scheduled workflows include:

- File organization
- Old-file archiving
- Duplicate detection

Scheduled organizer and archiver workflows still require permission validation, preview, and explicit user approval before moving files.

Scheduled duplicate detection remains read-only.

**Important:** The scheduler does not run continuously in the background. Users must launch SecureFlow and select option `4` to check and process due schedules.

### Workflow Preview and Approval

For file-moving workflows, SecureFlow:

1. Generates a list of proposed file actions.
2. Displays each action's source and destination.
3. Checks whether each action is permitted.
4. Labels actions as `ALLOWED` or `BLOCKED`.
5. Displays the number of allowed and blocked actions.
6. Requests approval for allowed actions only.
7. Executes permitted actions only after approval.
8. Records blocked or cancelled actions through the audit logger.

Example preview:

```text
=== WORKFLOW PREVIEW ===
Total proposed actions: 2

Action 1
Source:      test_files/example.txt
Destination: test_files/txt/example.txt
Status:      ALLOWED

Action 2
Source:      test_files/old.txt
Destination: test_files/archive/old.txt
Status:      BLOCKED

=== PREVIEW SUMMARY ===
Allowed actions: 1
Blocked actions: 1

Approve 1 permitted file action(s)? (y/n):
```

Entering `y` or `yes` approves permitted actions.

Entering `n` or `no` cancels the workflow without executing proposed file moves.

Invalid responses prompt the user to enter a valid answer.

If no actions are proposed, SecureFlow reports that there are no proposed file actions.

If all proposed actions are blocked, no approval is requested.

## Security Design

SecureFlow separates automation workflows, permission checking, configuration management, workflow previewing, user approval, file execution, audit logging, and scheduling into independent components.

### Workflow Management

The workflow manager selects the requested automation and generates workflow results.

File-moving workflows return proposed actions that are passed to the preview and approval controller.

Duplicate detection returns read-only results that are displayed without using the file-moving executor.

### Permission Validation

The permission checker validates file-moving actions against an authorized directory and configured security restrictions.

Checks include:

- Source and destination paths must resolve within the authorized directory.
- The source must be an existing regular file.
- Direct symbolic-link sources are rejected.
- Symbolic-link destinations are rejected.
- Existing destination files cannot be overwritten.
- Source file extensions must be permitted by configuration.
- Source file sizes must not exceed the configured limit.

The configured allowed folder is used when no folder is explicitly supplied to the permission checker.

Existing callers may supply an allowed folder directly.

### Preview and Approval

The `security/preview.py` module evaluates proposed actions and separates them into allowed and blocked groups.

The `security/approval.py` module handles user confirmation.

The `security/approval_executor.py` module coordinates:

- Preview generation
- Permission-based action filtering
- User approval
- Workflow cancellation
- Blocked and cancelled action logging
- Execution of approved actions
- Execution summaries

Blocked actions are not submitted to the file executor.

Cancelled actions are not executed.

### File Execution

The executor performs an additional permission check after preparing the destination directory and before creating the destination hard link.

File-moving operations use hard-link creation followed by source deletion.

This approach avoids directly overwriting an existing destination, but it does not provide a fully atomic move.

### Audit Logging

SecureFlow attempts to record file-operation outcomes through `security/audit_logger.py`.

Supported statuses include:

- `SUCCESS` — A file operation completed.
- `BLOCKED` — A requested action was rejected.
- `FAILED` — A supported filesystem error prevented completion.
- `CANCELLED` — The user declined approval for a permitted action.

Audit logging is best-effort.

If an audit-log write raises an `OSError`, the system reports a warning while preserving the underlying file-operation result.

The audit log is not guaranteed to be complete or tamper-resistant.

### Scheduling Architecture

Scheduling functionality is separated into four modules:

- `scheduler/schedule_config.py` — Loads and validates schedule definitions.
- `scheduler/schedule_manager.py` — Determines which schedules are due.
- `scheduler/schedule_history.py` — Loads and saves previously processed schedule timestamps.
- `scheduler/scheduled_runner.py` — Coordinates due workflow execution and scheduling history updates.

Schedule definitions are stored in `config/schedules.json`.

Scheduling history is stored in `logs/schedule_history.json`.

The scheduler uses timezone-aware UTC timestamps to calculate elapsed intervals.

## Version 0.2 — Security Testing

Version 0.2 introduced automated security testing using Python's built-in `unittest` framework.

The original six permission security tests covered:

1. Authorized file operations
2. Unauthorized destination paths
3. Overwrite prevention
4. Path traversal attempts
5. Symbolic-link destinations
6. Symbolic-link source files

These tests established the initial security-validation baseline.

## Version 0.3 — Multiple Automation Workflows

Version 0.3 expanded SecureFlow from a basic file organizer into a platform supporting three automation workflows.

### File Organizer

Organizes files into folders according to their file extensions.

### Old-File Archiver

Identifies files based on their last modification date and proposes moving older files into an archive folder.

Users choose how many days old a file must be before it qualifies for archiving.

### Duplicate File Detector

Calculates SHA-256 hashes to identify files with matching contents.

Reports original and duplicate file paths without automatically deleting, overwriting, or moving files.

### Workflow Manager

A centralized workflow manager connects the automation modules to a command-line selection menu.

Users can select workflows without modifying the source code.

## Version 0.4 — Configurable Security Policies

Version 0.4 introduced configurable security restrictions.

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

The `config/config_loader.py` module reads the JSON configuration file and validates required settings.

Validation includes:

- Confirming that the configuration is a JSON object.
- Requiring a non-empty allowed-folder string.
- Requiring a non-empty list of file extensions.
- Checking that each extension begins with a period.
- Requiring a positive numeric maximum file size.
- Reporting missing configuration files and invalid JSON.

### Permission Enforcement

The permission checker uses these settings to:

- Block source files with disallowed extensions.
- Block source files exceeding the maximum size.
- Continue enforcing authorized paths, symbolic-link restrictions, and overwrite prevention.

### Security Testing

Version 0.4 added two permission tests:

1. Blocking disallowed file extensions.
2. Blocking oversized files.

This increased the permission security suite from six to eight tests.

### Configuration Limitations

The configuration system provides basic security controls but is not a complete policy-enforcement framework.

File-extension restrictions check filenames rather than actual file contents.

File-size and filesystem checks may become outdated if files change between validation and execution.

An explicitly supplied allowed-folder argument can override the configured folder.

## Version 0.5 — Safer File Execution

Version 0.5 introduced structured filesystem error handling, additional permission validation, improved audit logging, and automated executor tests.

### Custom File-Operation Exception

The `security/exceptions.py` module defines `FileOperationError`.

This custom exception provides a consistent application-specific way to report supported filesystem operation failures.

### Structured Error Handling

The executor handles:

- **Missing files:** Reports missing source files or required paths.
- **Permission-denied errors:** Reports filesystem permission failures.
- **Existing destinations:** Blocks operations that would overwrite files.
- **Destination-folder creation failures:** Reports errors while preparing destination directories.
- **General filesystem errors:** Converts operating-system errors into `FileOperationError`.
- **Cross-filesystem moves:** Detects `errno.EXDEV` and reports that cross-filesystem moves are unsupported.

### Additional Permission Validation

The executor performs two permission checks:

1. Before beginning the file operation.
2. After creating the destination directory and before creating the destination hard link.

The second check can detect some changes to file paths or permissions between validation and execution.

However, repeated validation does not eliminate time-of-check-to-time-of-use (TOCTOU) race conditions.

### Hard-Link-Based File Execution

File moves use the following sequence:

1. Validate the requested action.
2. Prepare the destination directory.
3. Revalidate the requested action.
4. Create a hard link at the destination.
5. Delete the original source path.
6. Attempt to record the operation result.

Hard-link creation avoids directly overwriting an existing destination.

However, the overall move is not atomic.

If source deletion fails after hard-link creation, both source and destination paths may remain.

The executor does not automatically roll back partial operations.

Hard links cannot be created across different filesystems, so cross-filesystem moves are unsupported.

### Audit Logging Error Handling

The executor attempts to log successful, blocked, and failed file operations.

If writing a `FAILED` audit event raises an `OSError`, the executor prints a warning and preserves the original filesystem failure as `FileOperationError`.

If writing a `BLOCKED` event fails, the executor prints a warning and still returns `False`.

If a move succeeds but writing its `SUCCESS` event fails, the executor prints a warning and still returns `True`.

Audit-log write failures therefore do not incorrectly change the reported file-operation outcome.

### Executor Security Tests

Version 0.5 introduced `tests/test_executor.py`.

The three executor tests cover:

1. **Filesystem failure:** Simulates a disk error during hard-link creation and verifies that `FileOperationError` is raised.
2. **Source deletion failure:** Simulates a permission error during source deletion and verifies that both paths remain.
3. **Audit logging failure:** Simulates simultaneous filesystem and audit-log errors and verifies that the original filesystem error is preserved.

The tests use temporary directories and Python's `unittest.mock` module.

By the end of v0.5, the automated suite contained 11 tests:

| Test category | Tests |
|---|---:|
| Permission security | 8 |
| Executor failure handling | 3 |
| **Total** | **11** |

## Version 0.6 — Workflow Preview and Approval

Version 0.6 introduced a security checkpoint between workflow planning and file execution.

Users can review proposed file changes and explicitly approve or reject permitted actions before any files are moved.

### Workflow Preview Module

The `security/preview.py` module provides:

- `preview_action()` — Displays a proposed action and checks whether it is permitted.
- `preview_actions()` — Previews multiple actions and separates them into allowed and blocked groups.

Each preview displays:

- Source path
- Destination path
- Permission status

The preview summary displays the number of allowed and blocked actions.

### User Approval Module

The `security/approval.py` module provides `request_approval()`.

It:

- Requests confirmation before executing permitted file moves.
- Accepts `y`, `yes`, `n`, and `no`.
- Repeats the prompt when invalid input is entered.
- Returns `False` when there are no permitted actions to approve.

Approval is required for permitted file-moving actions.

### Approval and Execution Controller

The `security/approval_executor.py` module provides `execute_approved_actions()`.

This controller:

1. Receives proposed file actions.
2. Previews and checks the actions.
3. Records blocked actions as `BLOCKED`.
4. Requests approval only for permitted actions.
5. Records declined actions as `CANCELLED`.
6. Executes approved actions through the existing secure executor.
7. Reports the number of successful and unsuccessful actions.

The controller also handles supported `FileOperationError` exceptions so an execution failure can be reported without stopping the entire approved workflow.

### Command-Line Integration

The main application routes file-moving workflows through the approval controller.

The organizer and archiver use the preview and approval process.

The duplicate detector remains read-only and displays its results without requesting file-move approval.

### Cancellation Behavior

If the user declines approval:

- No permitted actions are executed.
- Proposed file moves are cancelled.
- Cancelled actions are submitted to the audit logger.
- The program reports that the workflow was cancelled.

This gives users an opportunity to reject unexpected changes before execution.

### Blocked Actions

Actions that fail permission checks are labeled `BLOCKED`.

Blocked actions:

- Are excluded from the approval request.
- Are not executed.
- Are submitted to the audit logger.

If no permitted actions remain, the workflow ends without requesting approval.

### Automated Tests

Version 0.6 added 14 tests across three new test files.

**`tests/test_preview.py` — 3 tests**

- Permitted actions are marked as allowed.
- Unauthorized actions are marked as blocked.
- Mixed actions are correctly separated into allowed and blocked groups.

**`tests/test_approval.py` — 4 tests**

- Approval with `y`.
- Rejection with `n`.
- Invalid input followed by valid approval.
- No approval prompt when the action count is zero.

**`tests/test_approval_executor.py` — 7 tests**

- Approved actions are executed.
- Rejected actions are not executed.
- Blocked actions are not executed.
- Empty workflows do not request approval or execute actions.
- Supported execution errors are handled.
- Cancelled workflows preserve source files.
- Approved workflows move files successfully.

By the end of v0.6, the test suite contained **25 tests**.

### Manual Workflow Verification

Version 0.6 was manually tested through the command-line interface.

**Organizer cancellation**

- Two permitted file moves appeared in the preview.
- The user entered `n`.
- The workflow was cancelled without moving the files.

**Organizer approval**

- Two permitted file moves appeared in the preview.
- The user entered `y`.
- Both files were successfully moved.
- The execution summary reported two successful actions and zero unsuccessful actions.

**Archiver with no proposed actions**

- The archiver was run with a one-day age threshold.
- No qualifying file actions were initially proposed.
- The workflow ended without requesting approval.

**Archiver with an existing destination**

- An old test file was identified for archiving.
- The proposed destination already contained a file with the same name.
- SecureFlow marked the action as `BLOCKED`.
- The existing destination file was not overwritten.

**Archiver with mixed allowed and blocked actions**

- A uniquely named old test file was marked `ALLOWED`.
- A conflicting file move was marked `BLOCKED`.
- SecureFlow requested approval for only the permitted action.
- After approval, the permitted file was moved successfully.
- The execution summary reported one successful action and zero unsuccessful actions.

These checks verified that the preview, permission filtering, approval, cancellation, and execution features worked together in the tested scenarios.

### Security Limitations

The v0.6 approval system adds user control but does not eliminate all filesystem risks.

Known limitations include:

- Previewed file paths and filesystem state may change before execution.
- Repeated permission checks do not eliminate TOCTOU vulnerabilities.
- Approval confirms proposed actions but does not guarantee that filesystem state remains unchanged.
- File operations are not fully atomic.
- Partial moves are not automatically rolled back.
- Audit logging remains best-effort.
- The command-line approval process is interactive.
- Unexpected input or runtime exceptions may still propagate outside the supported error handlers.

SecureFlow remains a cybersecurity-focused prototype rather than a fully hardened filesystem sandbox.

## Version 0.7 — Scheduling and Automation

Version 0.7 introduces configurable, interval-based scheduling for SecureFlow's existing automation workflows.

The scheduling system allows users to define recurring workflows, track when schedules were last processed, and prevent workflows from running again before their configured intervals expire.

Scheduling is integrated into the existing command-line application.

### Schedule Configuration

Schedules are defined in:

`config/schedules.json`

Example configuration:

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

Each schedule includes:

- `name` — A unique, non-empty schedule identifier.
- `workflow` — One of `organize`, `archive`, or `duplicates`.
- `interval_minutes` — A positive whole-number interval between scheduled runs.
- `enabled` — A Boolean value indicating whether the schedule is active.
- `days_old` — A required positive whole number for archive schedules.

For reference:

- `1440` minutes = 1 day.
- `10080` minutes = 7 days.

### Schedule Configuration Validation

The `scheduler/schedule_config.py` module provides `load_schedules()`.

It validates:

- The schedule configuration is a JSON object.
- The `schedules` field contains a list.
- Every schedule is a JSON object.
- Schedule names are non-empty strings.
- Schedule names are unique.
- Workflow names are supported.
- Intervals are positive integers.
- Enabled values are Boolean.
- Archive schedules include a positive `days_old` value.

Invalid schedule configurations raise a `ValueError`.

### Schedule Manager

The `scheduler/schedule_manager.py` module determines which schedules are due.

It provides:

- `current_time()` — Returns the current UTC time.
- `is_schedule_due()` — Determines whether an individual schedule is due.
- `get_due_schedules()` — Filters a collection of schedules to find due workflows.

A schedule is due when:

1. It is enabled.
2. It has never been processed, or its configured interval has elapsed since its last recorded processing time.

Disabled schedules are skipped.

### Scheduling History

The `scheduler/schedule_history.py` module manages persistent schedule history.

It provides:

- `load_history()` — Reads previously recorded schedule timestamps.
- `save_history()` — Writes updated timestamps to disk.

History is stored in:

`logs/schedule_history.json`

Timestamps are stored in ISO 8601 format and normalized to UTC.

The history file is created when scheduled workflows are processed.

The runtime history file should be excluded from Git version control because it contains local execution state.

### Scheduled Workflow Runner

The `scheduler/scheduled_runner.py` module coordinates scheduled workflow execution.

It provides:

- `run_scheduled_workflow()` — Runs a configured workflow using the existing workflow manager.
- `run_due_schedules()` — Loads schedules, checks their history, processes due workflows, and updates timestamps.

The scheduled runner reuses the existing security workflow.

For organizer and archiver schedules:

1. Generate proposed file actions.
2. Display the workflow preview.
3. Separate allowed and blocked actions.
4. Request approval for permitted actions.
5. Execute approved actions using the secure executor.

For duplicate-detection schedules:

1. Scan for duplicate files.
2. Display the results.
3. Do not execute file moves or request file-move approval.

### CLI Integration

Version 0.7 adds a fourth menu option:

```text
4. Run due scheduled workflows
```

Selecting this option calls `run_due_schedules()`.

If schedules are due, SecureFlow processes them and reports the number processed.

Example:

```text
Scheduled workflow: daily_organizer

=== WORKFLOW PREVIEW ===
Total proposed actions: 1

Action 1
Source:      test_files/archive_test.txt
Destination: test_files/txt/archive_test.txt
Status:      ALLOWED

=== PREVIEW SUMMARY ===
Allowed actions: 1
Blocked actions: 0

Approve 1 permitted file action(s)? (y/n): n
Workflow cancelled. No files were moved.

Scheduled workflow: weekly_archiver

=== WORKFLOW PREVIEW ===
Total proposed actions: 1

Action 1
Source:      test_files/archive_test.txt
Destination: test_files/archive/archive_test.txt
Status:      BLOCKED

=== PREVIEW SUMMARY ===
Allowed actions: 0
Blocked actions: 1
No permitted actions to execute.

Scheduled workflows processed: 2
```

If no schedules are due, the program displays:

```text
No scheduled workflows are due.
```

### Scheduling and Approval Behavior

A scheduled workflow is recorded as processed after its workflow handler returns, even when:

- The user declines approval.
- All proposed file actions are blocked.
- No file moves are completed.

This prevents the same schedule from being immediately retried on the next CLI check.

Therefore, the message `Scheduled workflows processed` indicates how many scheduled workflows were handled, **not** how many completed successful file operations.

Scheduled workflows are not fully unattended because file-moving operations still require interactive user approval.

### Automated Scheduling Tests

Version 0.7 adds **14 tests** across three test files.

**`tests/test_schedule_config.py` — 5 tests**

- Loads valid schedule configurations.
- Rejects unsupported workflow names.
- Rejects invalid intervals.
- Rejects duplicate schedule names.
- Requires a valid `days_old` value for archive schedules.

**`tests/test_schedule_manager.py` — 5 tests**

- Identifies new schedules as due.
- Skips disabled schedules.
- Identifies schedules whose intervals have elapsed.
- Prevents schedules from running before their intervals expire.
- Filters due schedules correctly.

**`tests/test_scheduled_runner.py` — 4 tests**

- Runs due scheduled workflows.
- Routes organizer workflows through the approval controller.
- Keeps duplicate detection separate from the file executor.
- Handles cases where no schedules are due.

### Complete Automated Test Suite

The full test suite now contains:

| Test category | Tests |
|---|---:|
| Permission security tests | 8 |
| Executor failure tests | 3 |
| Workflow preview tests | 3 |
| User approval tests | 4 |
| Approval executor tests | 7 |
| Schedule configuration tests | 5 |
| Schedule manager tests | 5 |
| Scheduled runner tests | 4 |
| **Total** | **39** |

Run the complete test suite:

```bash
python3 -m unittest discover -s tests -v
```

Verified result:

```text
Ran 39 tests in 0.024s

OK
```

### Manual Scheduling Verification

Version 0.7 was also tested through the command-line interface.

**First scheduler run**

- The daily organizer schedule was due.
- One permitted file move appeared in the preview.
- The user declined approval.
- No files were moved.
- The weekly archiver schedule was also due.
- One archive action was blocked because the destination already existed.
- The blocked action was not executed.
- The scheduler reported two processed workflows.

**Second scheduler run**

The user immediately selected option `4` again.

SecureFlow displayed:

```text
No scheduled workflows are due.
```

This confirmed that scheduling history persisted between application runs and prevented premature workflow reruns.

### Scheduling Limitations

The v0.7 scheduler has the following limitations:

- Scheduling checks are manually triggered through the CLI.
- There is no always-running background scheduler or operating-system job integration.
- Scheduled file moves still require explicit user approval.
- A cancelled or blocked workflow is recorded as processed.
- Schedule history records processing timestamps rather than detailed success or failure results.
- If a workflow raises an unhandled exception before its history is saved, it may remain due.
- The history file does not provide locking for concurrent scheduler processes.
- Schedule configuration and history files are not tamper-resistant.
- Existing filesystem and audit-logging limitations still apply.

The scheduling system provides controlled interval-based automation rather than fully unattended background execution.

## Current Limitations

The platform currently has the following limitations:

- Advanced symbolic-link attacks and filesystem race conditions are not fully mitigated.
- Partial file operations do not have automatic rollback.
- Audit logging is best-effort rather than guaranteed.
- Audit records are not tamper-resistant.
- Cross-filesystem file moves are unsupported.
- Explicit allowed-folder overrides can bypass the configured folder restriction.
- File-extension checks do not inspect actual file contents.
- File-size checks may become outdated before execution.
- Duplicate detection examines only the top level of the selected folder.
- Matching SHA-256 hashes are not verified with a byte-for-byte comparison.
- Preview and approval are currently provided through the command-line interface.
- Scheduling requires manually selecting the scheduler option.
- Scheduled file moves require interactive approval.
- Schedule history does not record detailed workflow outcomes.
- There is no graphical dashboard yet.
- Integration and adversarial security testing remain limited.

These limitations require further review before production use.

## Future Development

Planned development milestones include:

- **v0.8 — Dashboard and Monitoring:** Build a graphical Python dashboard for managing workflows, reviewing previews, approving actions, and viewing audit activity.
- **v0.9 — Integration and Security Review:** Test workflows together, investigate security edge cases, and address remaining implementation weaknesses.
- **v1.0 — Final Release and Demo:** Finalize documentation, installation instructions, demonstrations, and release testing.

The long-term goal is a practical personal automation platform that combines useful workflows with transparent security controls, clear audit records, and predictable failure handling.