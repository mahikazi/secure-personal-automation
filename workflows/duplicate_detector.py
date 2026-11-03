from pathlib import Path
import hashlib

def detect_duplicates(folder):
    folder = Path(folder)
    file_hashes = {}
    duplicates = []

    for file in folder.iterdir():
        if not file.is_file() or file.is_symlink():
            continue

        sha256 = hashlib.sha256()

        with file.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)

        file_hash = sha256.hexdigest()

        if file_hash in file_hashes:
            original_file = file_hashes[file_hash]

            duplicates.append({
                "original": original_file,
                "duplicate": file
            })

            print(f"Duplicate found: {file.name}")

        else:
            file_hashes[file_hash] = file

    return duplicates