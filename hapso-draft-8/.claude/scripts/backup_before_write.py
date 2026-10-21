"""
Backup a file before Claude writes or edits it.

Usage:
    python3 .claude/scripts/backup_before_write.py <file_path>

Saves a timestamped copy to:
    .claude/backups/YYYY-MM-DD/HH-MM-SS_<original_path_flattened>
"""

import os
import shutil
import sys
from datetime import datetime


BACKUP_ROOT = ".claude/backups"
SKIP_PREFIXES = (".claude/backups", ".claude/trash", "__pycache__", ".git")


def flatten_path(path: str) -> str:
    return path.replace("/", "__").replace("\\", "__")


def backup(file_path: str) -> None:
    if not os.path.isfile(file_path):
        return

    for prefix in SKIP_PREFIXES:
        if file_path.startswith(prefix):
            return

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H-%M-%S")
    flat_name = time_str + "_" + flatten_path(file_path)

    dest_dir = os.path.join(BACKUP_ROOT, date_str)
    os.makedirs(dest_dir, exist_ok=True)

    dest_path = os.path.join(dest_dir, flat_name)
    shutil.copy2(file_path, dest_path)

    print(f"[BACKUP]: {file_path} → {dest_path}")


if len(sys.argv) < 2:
    sys.exit(0)

backup(sys.argv[1])
