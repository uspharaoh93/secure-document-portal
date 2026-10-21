"""Verify a backup and restored copy without replacing the running database."""

import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

from backup import copy_database

ROOT = Path(__file__).resolve().parent.parent
source = ROOT / ".local-data" / "portal.sqlite3"
if not source.is_file():
    raise SystemExit("Run scripts/setup_demo.py first.")
with tempfile.TemporaryDirectory(dir=source.parent) as directory:
    backup = Path(directory) / "backup.sqlite3"
    restored = Path(directory) / "restored.sqlite3"
    copy_database(source, backup)
    copy_database(backup, restored)
    with closing(sqlite3.connect(backup)) as a, closing(sqlite3.connect(restored)) as b:
        if list(a.iterdump()) != list(b.iterdump()):
            raise SystemExit("Restored database differs from the backup.")
print("Backup and restored copy match, including users, assignments and audit records.")
