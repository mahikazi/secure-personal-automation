from workflows.file_organizer import organize_files
from workflows.file_archiver import archive_old_files
from workflows.duplicate_detector import detect_duplicates

def run_workflow(workflow_name, folder, days_old=30):
    if workflow_name == "organize":
        return organize_files(folder)

    if workflow_name == "archive":
        return archive_old_files(folder, days_old)

    if workflow_name == "duplicates":
        return detect_duplicates(folder)

    return []