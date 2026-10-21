# Local operation and recovery

## Data location

Setup creates `.local-data/` with restrictive POSIX permissions. It holds the SQLite database, generated application secret and generated demonstration passwords. It is ignored by Git. Do not upload it, include it in screenshots or attach it to a bug report. On systems without POSIX permissions, apply equivalent user-only access controls.

The database includes fictional documents, account password hashes, sessions, assignments and audit records. The credentials JSON contains the generated demonstration passwords in plaintext for local walkthroughs; this convenience is not a production credential-delivery mechanism. Delete it when it is no longer needed, after retaining the passwords in your own password manager.

## Start, stop and restart

1. Activate `.venv` and run `python manage.py runserver 127.0.0.1:8000 --noreload`.
2. Stop with Ctrl+C. Do not bind to `0.0.0.0` or expose the server through a tunnel.
3. Start with the same command. SQLite preserves the documents, assignments and events. Setup is not required again.

## Backup and restore

1. Stop the demo for a simple, consistent operator workflow.
2. Create a backup inside the private directory:

   ```sh
   python scripts/backup.py .local-data/portal.sqlite3 .local-data/backup.sqlite3
   ```

3. Verify a restore to a new file:

   ```sh
   python scripts/backup.py .local-data/backup.sqlite3 .local-data/restored.sqlite3
   ```

   The command refuses to overwrite an existing destination and runs SQLite integrity checks. For a full logical-data comparison, use `python scripts/recovery_check.py`.

4. To actually return the application to that backup, keep the server stopped, rename the current database to a separate private recovery copy, then rename `restored.sqlite3` to `portal.sqlite3`. Keep the application secret available. Do not overwrite the only original copy.
5. Restart, sign in and verify document assignments. A restored database represents an earlier point in time; recent permission changes and audit events may be absent. Run `python manage.py clearsessions` only to remove expired sessions; if all sessions need revocation, use a reviewed administrative process to delete all session records. Do not assume a restore preserves recent revocations.

Backups are not encrypted by this project. Store them on encrypted, user-controlled storage. The automated restore check does not prove recovery from disk loss or a production outage.

## Changes and dependency maintenance

Change source on a branch, run all checks, and inspect the diff. The `.in` files describe dependency choices; `.txt` lockfiles include exact versions and hashes. Regenerate both with `pip-compile --generate-hashes --strip-extras` using Python 3.14, then install with `--require-hashes` and rerun checks. Review updates; a newer version is not automatically safer.

## Known operational limits

Audit events are shown as the latest 100 entries, but older records remain in the database. There is no retention job, centralized monitoring, password reset, login throttling, MFA, encrypted application storage or production web server. Use fictional data only.
