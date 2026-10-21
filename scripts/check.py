"""Run the local checks used by CI. Does not need seeded data or real credentials."""

import os
import secrets
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
environment = os.environ.copy()
environment["PORTAL_SECRET_KEY"] = secrets.token_urlsafe(64)
commands = [
    [sys.executable, "manage.py", "check"],
    [sys.executable, "manage.py", "makemigrations", "--check", "--dry-run"],
    [sys.executable, "manage.py", "test", "--verbosity", "2"],
    [sys.executable, "-m", "ruff", "check", "."],
    [sys.executable, "-m", "bandit", "-r", "portal,config", "-q"],
    [sys.executable, "-m", "pip_audit", "-r", "requirements.txt", "--disable-pip"],
    [sys.executable, "-m", "pip_audit", "-r", "requirements-dev.txt", "--disable-pip"],
]
for command in commands:
    subprocess.run(command, cwd=ROOT, env=environment, check=True)
