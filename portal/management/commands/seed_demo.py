import json
import os
import secrets

from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from portal.models import Document


class Command(BaseCommand):
    help = "Create fictional accounts and six documents in a fresh local database."

    def handle(self, *args, **options):
        credentials_path = settings.DATA_DIR / "credentials.json"
        if User.objects.exists():
            self.stdout.write("Accounts already exist; no accounts or passwords changed.")
            return
        if credentials_path.exists():
            raise CommandError("Credentials file already exists. Use a new demo directory.")
        credentials = {
            name: secrets.token_urlsafe(24)
            for name in ("employee.alex", "employee.jordan", "reviewer")
        }
        with transaction.atomic():
            users = {
                name: User.objects.create_user(name, password=password)
                for name, password in credentials.items()
            }
            users["reviewer"].user_permissions.add(
                Permission.objects.get(codename="view_auditevent")
            )
            titles = [
                "Welcome and orientation",
                "Sample meeting notes",
                "Practice project brief",
                "Sample handover checklist",
                "Fictional research summary",
                "Training schedule",
            ]
            for i, title in enumerate(titles):
                document = Document.objects.create(
                    title=title,
                    content=(
                        f"{title}\n\nFICTIONAL TRAINING RECORD {i + 1}\n\n"
                        "This record was written for a local security demonstration.\n"
                        "It contains no client information or proprietary material.\n\n"
                        "Task: review the sample, record a decision, and confirm the next step.\n"
                        "Status: ready for practice review.\n"
                    ),
                )
                owner = "employee.alex" if i < 3 else "employee.jordan"
                document.assigned_to.add(users[owner])
            descriptor = os.open(credentials_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w") as output:
                json.dump(credentials, output, indent=2)
        self.stdout.write("Created three accounts and six fictional documents.")
        self.stdout.write(
            "Credentials are in .local-data/credentials.json (keep this file private)."
        )
