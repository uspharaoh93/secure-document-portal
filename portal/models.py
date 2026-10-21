from django.conf import settings
from django.db import models


class Document(models.Model):
    title = models.CharField(max_length=160)
    content = models.TextField()
    assigned_to = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="documents")

    class Meta:
        ordering = ["pk"]


class AuditEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    actor_id = models.PositiveBigIntegerField(null=True)
    target_id = models.PositiveBigIntegerField(null=True)
    action = models.CharField(max_length=24)
    outcome = models.CharField(max_length=8)

    class Meta:
        ordering = ["-pk"]
        default_permissions = ("view",)
