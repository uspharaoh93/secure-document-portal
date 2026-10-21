from .models import AuditEvent

ACTIONS = {
    "document.list",
    "document.view",
    "document.download",
    "audit.view",
    "auth.login",
    "auth.logout",
}


def record(*, actor_id, action, outcome, target_id=None):
    """Accept identifiers and fixed codes only; never accept a request or document body."""
    if action not in ACTIONS or outcome not in {"allow", "deny"}:
        raise ValueError("Unknown audit event")
    # SQLite integers have a signed 64-bit limit; untrusted URL IDs can be larger.
    if target_id is not None and not 0 <= target_id <= 2**63 - 1:
        target_id = None
    return AuditEvent.objects.create(
        actor_id=actor_id, target_id=target_id, action=action, outcome=outcome
    )
