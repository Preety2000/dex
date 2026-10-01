import os
import shutil
from pathlib import Path


from pathlib import Path
import shutil


def remove_pycache(folder):
    """पूरी directory hierarchy में __pycache__ के सभी folders और files delete करता है."""
    folder = Path(folder)

    def remove_readonly(func, path, exc_info):
        """Read-only होने पर permission हटाकर दोबारा delete करता है."""
        try:
            os.chmod(path, 0o777)
            func(path)
        except Exception as e:
            print(f"Could not force delete {path}: {e}")

    # सबसे पहले सभी __pycache__ खोजें
    for p in list(folder.rglob("__pycache__")):
        try:
            if p.is_dir():
                # Folder और उसके अंदर की सभी files delete
                shutil.rmtree(p, onerror=remove_readonly)
                print(f"Deleted folder: {p}")

            elif p.is_file():
                try:
                    os.chmod(p, 0o777)
                except Exception:
                    pass

                p.unlink()
                print(f"Deleted file: {p}")

        except Exception as e:
            print(f"Could not delete {p}: {e}")


def print_tree(folder, prefix="", file_handle=None):
    folder = Path(folder)

    try:
        items = sorted(folder.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    except PermissionError:
        return

    for i, item in enumerate(items):
        last = i == len(items) - 1
        connector = "└── " if last else "├── "
        line = prefix + connector + item.name

        # Terminal par print karein
        print(line)

        # File me write karein
        if file_handle:
            file_handle.write(line + "\n")

        if item.is_dir():
            new_prefix = prefix + ("    " if last else "│   ")
            print_tree(item, new_prefix, file_handle)


# Path setup
folder_path = os.getcwd()
output_file = Path(folder_path) / "folder_tree.txt"

# Pehle sabhi __pycache__ folders ko delete karein
print("--- Cleaning __pycache__ folders ---")
remove_pycache(folder_path)
print("------------------------------------\n")

# Ab tree structure print aur save karein
print(f"Directory: {folder_path}\n")

with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"Directory: {folder_path}\n\n")
    print_tree(folder_path, file_handle=f)
