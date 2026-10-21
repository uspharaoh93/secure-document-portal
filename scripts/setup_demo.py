"""Initialize local-only data. Re-running does not reset credentials or records."""

import os
import secrets
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.umask(0o077)
data = ROOT / ".local-data"
data.mkdir(mode=0o700, exist_ok=True)
data.chmod(0o700)
secret = data / "secret.key"
if not secret.exists():
    descriptor = os.open(secret, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as output:
        output.write(secrets.token_urlsafe(64))
for command in ("migrate", "seed_demo"):
    subprocess.run([sys.executable, "manage.py", command], cwd=ROOT, check=True)
print("Start: python manage.py runserver 127.0.0.1:8000 --noreload")
