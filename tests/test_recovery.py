import os
import sqlite3
import tempfile
from pathlib import Path
from unittest import TestCase

from scripts.backup import copy_database


class RecoveryTests(TestCase):
    def test_backup_restores_exact_data_and_restricts_file(self):
        with tempfile.TemporaryDirectory() as directory:
            source, backup, restored = [
                Path(directory) / name for name in ["source.db", "backup.db", "restored.db"]
            ]
            with sqlite3.connect(source) as db:
                db.execute("CREATE TABLE records (id INTEGER PRIMARY KEY, content TEXT)")
                db.execute("INSERT INTO records VALUES (1, ?)", ("fictional record",))
            copy_database(source, backup)
            copy_database(backup, restored)
            with sqlite3.connect(restored) as db:
                self.assertEqual(
                    db.execute("SELECT * FROM records").fetchall(), [(1, "fictional record")]
                )
            if os.name == "posix":
                self.assertEqual(restored.stat().st_mode & 0o777, 0o600)

    def test_existing_destination_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.db"
            with sqlite3.connect(source) as db:
                db.execute("CREATE TABLE records (id INTEGER)")
            target = Path(directory) / "existing.db"
            target.write_bytes(b"keep this")
            with self.assertRaises(FileExistsError):
                copy_database(source, target)
            self.assertEqual(target.read_bytes(), b"keep this")

    def test_missing_source_does_not_create_empty_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "backup.db"
            with self.assertRaises(FileNotFoundError):
                copy_database(Path(directory) / "missing.db", target)
            self.assertFalse(target.exists())
