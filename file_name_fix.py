# -*- coding: utf-8 -*-

"""
SMART PROJECT NAME FIXER
========================

यह script:
1. Project में typo वाले file/folder names खोजता है।
2. Safe names को automatically rename करता है।
3. Rename से पहले backup बनाता है।
4. Code/HTML/JS/CSS/JSON आदि में references update करता है।
5. Existing target होने पर overwrite नहीं करता।
6. Windows permission/read-only समस्या को handle करने की कोशिश करता है।

IMPORTANT:
- DRY_RUN = False होने पर actual rename होगा।
- CREATE_BACKUP = True होने पर पहले backup बनेगा।
"""

import os
import re
import sys
import shutil
import stat
from pathlib import Path
from datetime import datetime

# =========================================================
# PROJECT
# =========================================================

PROJECT_ROOT = Path(r"C:\Users\DELL\OneDrive\Documents\Myfile")

# TRUE = केवल report
# FALSE = ACTUAL RENAME
DRY_RUN = False

# Rename से पहले backup
CREATE_BACKUP = True


# =========================================================
# SKIP DIRECTORIES
# =========================================================

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    # User/generated media को अभी सुरक्षित रखें
    "uploads",
    "media",
    "db_media",
    "ex_context",
    "exnr",
}


# =========================================================
# TEXT FILE EXTENSIONS
# =========================================================

TEXT_EXTENSIONS = {
    ".py",
    ".html",
    ".htm",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".css",
    ".scss",
    ".json",
    ".sql",
    ".yml",
    ".yaml",
    ".txt",
    ".md",
    ".xml",
    ".ini",
    ".cfg",
    ".bat",
    ".conf",
}


# =========================================================
# SAFE RENAME MAP
# =========================================================

SAFE_RENAME_MAP = {
    # -------------------------
    # Root / Docker
    "practice.py": "practice.py",
    "practice.html": "practice.html",
    "practice.js": "practice.js",
    "practice.css": "practice.css",
    # -------------------------
    "doker-compose.yml": "docker-compose.yml",
    # -------------------------
    # Text / Database
    # -------------------------
    "rule_for_mcq.txt": "rule_for_mcq.txt",
    # -------------------------
    # Python
    # -------------------------
    "insert.py": "insert.py",
    "entry.py": "entry.py",
    "secondary.py": "secondary.py",
    "exam_controller.py": "exam_controller.py",
    "answer_sheet.py": "answer_sheet.py",
    # -------------------------
    # API / folders
    # -------------------------
    "chat": "chat",
    "socket": "socket",
    # -------------------------
    # CSS
    # -------------------------
    "article.css": "article.css",
    # -------------------------
    # JavaScript
    # -------------------------
    "form_backup.js": "form_backup.js",
    "backup.js": "backup.js",
    # -------------------------
    # JSON
    # -------------------------
    "exam_context.json": "exam_context.json",
    # -------------------------
    # Images
    # -------------------------
    "syllbus.png": "syllabus.png",
    # -------------------------
    # SVG
    # -------------------------
    "about.svg": "about.svg",
    "categories.svg": "categories.svg",
    "ic_hand.svg": "ic_hand.svg",
    "ic_rotate_left.svg": "ic_rotate_left.svg",
    "ic_rotate_right.svg": "ic_rotate_right.svg",
    "user_message.svg": "user_message.svg",
    # -------------------------
    # HTML
    # -------------------------
    "backup.html": "backup.html",
    "dashboard.html": "dashboard.html",
    "teacher_verify_identity.html": "teacher_verify_identity.html",
    "second_parameter.html": "second_parameter.html",
    "list_category.html": "list_category.html",
    "send_messages.html": "send_messages.html",
    "send_email.html": "send_email.html",
    "answer_sheet.html": "answer_sheet.html",
    # -------------------------
    # SQL
    # -------------------------
    "result_tamp.sql": "result_temp.sql",
    "verify_indentity.sql": "verify_identity.sql",
}


# =========================================================
# ONLY REVIEW - AUTO RENAME नहीं
# =========================================================

REVIEW_ONLY_NAMES = {
    "chat",
    "socket",
    "fimeg",
    "exm",
    "meb",
    "req",
    "rqh",
    "qs",
    "dm",
    "stp_tamp",
    "stuexses",
    "i_be_index,js",
    "aapage_e",
    "lolo",
}


# =========================================================
# FILES
# =========================================================

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

PLAN_FILE = PROJECT_ROOT / "RENAME_PLAN.txt"

LOG_FILE = PROJECT_ROOT / "RENAME_LOG.txt"

REVIEW_FILE = PROJECT_ROOT / "RENAME_REVIEW_REQUIRED.txt"


# =========================================================
# HELPERS
# =========================================================


def is_skipped(path: Path) -> bool:
    """
    Skip folders के अंदर की files को ignore करता है।
    """

    try:
        relative = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return True

    return any(
        part.lower() in {x.lower() for x in SKIP_DIRS} for part in relative.parts
    )


def get_paths():
    """
    Project के सभी paths देता है।
    """

    if not PROJECT_ROOT.exists():
        raise FileNotFoundError(f"Project folder not found:\n{PROJECT_ROOT}")

    return [path for path in PROJECT_ROOT.rglob("*") if not is_skipped(path)]


def force_remove_readonly(func, path, exc_info):
    """
    Windows read-only files/folders के लिए retry.
    """

    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        try:
            os.chmod(path, 0o777)
            func(path)
        except Exception as exc:
            print(f"Permission error: {path}\n" f"Reason: {exc}")


def safe_rename(old_path: Path, new_path: Path):
    """
    Windows-safe rename.
    """

    if not old_path.exists():
        raise FileNotFoundError(f"Old path not found: {old_path}")

    if new_path.exists():
        raise FileExistsError(f"Target already exists: {new_path}")

    try:
        old_path.rename(new_path)
        return True

    except PermissionError:

        # Read-only attribute हटाने की कोशिश
        try:
            os.chmod(old_path, stat.S_IWRITE)
        except Exception:
            pass

        try:
            old_path.rename(new_path)
            return True

        except PermissionError as exc:
            raise PermissionError(
                f"Windows ने rename permission deny की:\n"
                f"{old_path}\n\n"
                f"अगर file किसी program में खुली है तो उसे बंद करें।"
            ) from exc


# =========================================================
# COLLECT OPERATIONS
# =========================================================


def collect_operations():

    operations = []
    review_items = []

    paths = get_paths()

    # Deepest path पहले
    paths.sort(key=lambda item: len(item.parts), reverse=True)

    for path in paths:

        name = path.name

        # -------------------------------------
        # SAFE RENAME
        # -------------------------------------

        if name in SAFE_RENAME_MAP:

            new_name = SAFE_RENAME_MAP[name]

            new_path = path.with_name(new_name)

            if new_path.exists():

                status = "CONFLICT"

                reason = "Target already exists"

            else:

                status = "READY"

                reason = "Safe rename"

            operations.append(
                {
                    "status": status,
                    "old": path,
                    "new": new_path,
                    "reason": reason,
                }
            )

        # -------------------------------------
        # REVIEW ONLY
        # -------------------------------------

        if path.stem.lower() in {
            x.lower() for x in REVIEW_ONLY_NAMES
        } or name.lower() in {x.lower() for x in REVIEW_ONLY_NAMES}:
            review_items.append(path)

    return operations, review_items


# =========================================================
# REPORT
# =========================================================


def write_reports(operations, review_items):

    plan_lines = [
        "SMART PROJECT NAME FIXER",
        "SAFE RENAME PLAN",
        f"Generated: {datetime.now()}",
        "=" * 100,
        "",
    ]

    for item in operations:

        plan_lines.append(f"[{item['status']}] " f"{item['old']} -> {item['new']}")

        plan_lines.append(f"    Reason: {item['reason']}")

    if not operations:
        plan_lines.append("No safe spelling corrections found.")

    PLAN_FILE.write_text("\n".join(plan_lines), encoding="utf-8")

    review_lines = [
        "MANUAL REVIEW REQUIRED",
        f"Generated: {datetime.now()}",
        "=" * 100,
        "",
        "इन names को automatically rename नहीं किया गया:",
        "",
    ]

    for path in review_items:
        review_lines.append(str(path))

    REVIEW_FILE.write_text("\n".join(review_lines), encoding="utf-8")


# =========================================================
# BACKUP
# =========================================================


def create_backup():

    backup_path = PROJECT_ROOT.parent / (f"{PROJECT_ROOT.name}_backup_{TIMESTAMP}")

    print("Backup बनाया जा रहा है...")
    print(backup_path)

    shutil.copytree(
        PROJECT_ROOT,
        backup_path,
        ignore=shutil.ignore_patterns(
            ".git",
            ".venv",
            "venv",
            "env",
            "__pycache__",
            "node_modules",
            "uploads",
            "media",
            "db_media",
        ),
    )

    return backup_path


# =========================================================
# REFERENCE UPDATE
# =========================================================


def update_references(rename_pairs):

    updated_files = []
    errors = []

    if not rename_pairs:
        return updated_files, errors

    print("References update किए जा रहे हैं...")

    for file_path in get_paths():

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in TEXT_EXTENSIONS:
            continue

        try:

            original = file_path.read_text(encoding="utf-8")

        except (
            UnicodeDecodeError,
            PermissionError,
            OSError,
        ):
            continue

        updated = original

        for old_name, new_name in rename_pairs:

            # Exact filename reference
            pattern = rf"(?<![\w.-])" rf"{re.escape(old_name)}" rf"(?![\w.-])"

            updated = re.sub(
                pattern,
                lambda match: new_name,
                updated,
            )

        if updated != original:

            try:

                file_path.write_text(updated, encoding="utf-8")

                updated_files.append(file_path)

                print(f"  Reference updated: " f"{file_path}")

            except OSError as exc:

                errors.append(f"{file_path}: {exc}")

    return updated_files, errors


# =========================================================
# LOG
# =========================================================


def append_log(message):

    try:

        with LOG_FILE.open("a", encoding="utf-8") as log:

            log.write(f"[{datetime.now()}] " f"{message}\n")

    except Exception as exc:

        print(f"Log write error: {exc}")


# =========================================================
# MAIN
# =========================================================


def main():

    print("=" * 80)
    print("SMART PROJECT NAME FIXER")
    print("=" * 80)

    print(f"Project:\n{PROJECT_ROOT}")

    print(f"\nDRY_RUN = {DRY_RUN}")

    try:

        operations, review_items = collect_operations()

    except FileNotFoundError as exc:

        print(exc)
        sys.exit(1)

    write_reports(operations, review_items)

    print(f"Plan: {PLAN_FILE}")

    print(f"Review: {REVIEW_FILE}")

    print("-" * 80)

    if operations:

        for item in operations:

            print(
                f"[{item['status']}] "
                f"{item['old'].name} "
                f"-> "
                f"{item['new'].name}"
            )

            if item["status"] == "CONFLICT":

                print(f"    ! {item['reason']}")

    else:

        print("कोई safe rename नहीं मिला।")

    print("-" * 80)

    ready = [item for item in operations if item["status"] == "READY"]

    conflicts = [item for item in operations if item["status"] == "CONFLICT"]

    print(f"Total suggestions : {len(operations)}")

    print(f"Ready to rename   : {len(ready)}")

    print(f"Conflicts         : {len(conflicts)}")

    print(f"Manual review     : {len(review_items)}")

    # =====================================================
    # DRY RUN
    # =====================================================

    if DRY_RUN:

        print("DRY_RUN=True")

        print("कोई actual rename नहीं किया गया।")

        return

    # =====================================================
    # NOTHING TO RENAME
    # =====================================================

    if not ready:

        print("Rename करने के लिए कोई READY file नहीं है।")

        if conflicts:

            print("कुछ files के target पहले से मौजूद हैं।")

        return

    # =====================================================
    # BACKUP
    # =====================================================

    if CREATE_BACKUP:

        try:

            backup_path = create_backup()

            print(f"Backup complete:\n" f"{backup_path}")

        except Exception as exc:

            print("BACKUP ERROR:")

            print(exc)

            print("Safety के लिए rename रोक दिया गया।")

            return

    # =====================================================
    # RENAME
    # =====================================================

    rename_pairs = []

    renamed_count = 0
    failed_count = 0

    print("=" * 80)
    print("RENAMING STARTED")
    print("=" * 80)

    for item in ready:

        old_path = item["old"]
        new_path = item["new"]

        try:

            safe_rename(old_path, new_path)

            rename_pairs.append(
                (
                    old_path.name,
                    new_path.name,
                )
            )

            renamed_count += 1

            append_log(f"RENAMED: " f"{old_path} -> {new_path}")

            print(f"OK: " f"{old_path.name} " f"-> " f"{new_path.name}")

        except Exception as exc:

            failed_count += 1

            append_log(f"RENAME ERROR: " f"{old_path} -> " f"{new_path} | {exc}")

            print(f"ERROR: {old_path}")

            print(f"       {exc}")

    # =====================================================
    # UPDATE REFERENCES
    # =====================================================

    updated_files = []
    errors = []

    if rename_pairs:

        updated_files, errors = update_references(rename_pairs)

    # =====================================================
    # FINAL LOG
    # =====================================================

    for file_path in updated_files:

        append_log(f"REFERENCE UPDATED: " f"{file_path}")

    for error in errors:

        append_log(f"REFERENCE ERROR: " f"{error}")

    append_log(f"FINISHED: " f"{datetime.now()}")

    # =====================================================
    # RESULT
    # =====================================================

    print("=" * 80)
    print("RENAME COMPLETE")
    print("=" * 80)

    print(f"Renamed files/folders : " f"{renamed_count}")

    print(f"Failed                : " f"{failed_count}")

    print(f"References updated    : " f"{len(updated_files)}")

    print(f"Reference errors      : " f"{len(errors)}")

    print(f"Plan  : {PLAN_FILE}")

    print(f"Log   : {LOG_FILE}")

    print(f"Review: {REVIEW_FILE}")

    print("काम पूरा हुआ।")


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    main()
