"""
Intercept rm commands and move files to .claude/trash instead of deleting.

Usage:
    python3 .claude/scripts/intercept_delete.py <bash_command>

If the command contains 'rm ', affected files are moved to:
    .claude/trash/YYYY-MM-DD/HH-MM-SS_<original_path_flattened>

Prints a warning so Claude knows to use this path instead of rm.
"""

import os
import re
import shutil
import sys
from datetime import datetime


TRASH_ROOT = ".claude/trash"


def flatten_path(path: str) -> str:
    return path.replace("/", "__").replace("\\", "__")


def move_to_trash(file_path: str) -> None:
    file_path = file_path.strip().strip("'\"")

    if not os.path.exists(file_path):
        return

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H-%M-%S")
    flat_name = time_str + "_" + flatten_path(file_path)

    dest_dir = os.path.join(TRASH_ROOT, date_str)
    os.makedirs(dest_dir, exist_ok=True)

    dest_path = os.path.join(dest_dir, flat_name)
    shutil.move(file_path, dest_path)

    print(f"[TRASH]: {file_path} → {dest_path}")


def intercept(command: str) -> None:
    if "rm " not in command:
        return

    # Extract file paths from rm command (skip flags like -rf)
    tokens = command.split()
    paths = [t for t in tokens if not t.startswith("-") and t != "rm"]

    if not paths:
        return

    print(f"[TRASH]: Intercepted rm — moving to trash instead.")
    for path in paths:
        move_to_trash(path)

    # Exit with non-zero to block the actual rm from running
    sys.exit(1)


if len(sys.argv) < 2:
    sys.exit(0)

intercept(sys.argv[1])
