from pathlib import Path
from datetime import datetime, timedelta

def archive_old_files(folder, days_old=30):
    folder = Path(folder)
    actions = []

    cutoff_date = datetime.now() - timedelta(days=days_old)

    for file in folder.iterdir():
        if not file.is_file():
            continue

        modified_date = datetime.fromtimestamp(file.stat().st_mtime)

        if modified_date < cutoff_date:
            destination = folder / "archive" / file.name

            action = {
                "source": file,
                "destination": destination
            }

            actions.append(action)

    return actions