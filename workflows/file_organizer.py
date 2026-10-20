from pathlib import Path

def organize_files(folder_path):
    folder = Path(folder_path)
    proposed_actions = []

    for item in folder.iterdir():
        if item.is_file():
            category = item.suffix.lower().replace(".", "") or "other"
            destination = folder / category / item.name

            action = {
                "source": str(item),
                "destination": str(destination)
            }

            proposed_actions.append(action)

    return proposed_actions