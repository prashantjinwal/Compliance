"""
audit/utils.py

Single entry-point for writing audit log entries.
Import and call log_action() from any view or service layer.
"""

import logging

logger = logging.getLogger(__name__)


def log_action(
    user,
    action: str,
    entity_type: str,
    entity_id: str,
    description: str,
    organization=None,
    metadata: dict | None = None,
    request=None,
):
    """
    Create an AuditLog record.

    Args:
        user        : User instance (or None for system actions)
        action      : One of AuditLog.ACTION_CHOICES keys
        entity_type : String name of the model (e.g. "Regulation")
        entity_id   : String PK of the entity
        description : Human-readable description
        organization: Organization instance (falls back to user.organization)
        metadata    : Arbitrary dict to store alongside the log
        request     : Optional DRF/Django request — used to capture IP address
    """
    try:
        from audit.models import AuditLog  # late import to avoid circular deps

        org = organization or (user.organization if user else None)

        ip_address = None
        if request:
            ip_address = _get_client_ip(request)

        AuditLog.objects.create(
            organization=org,
            user=user,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id),
            description=description,
            metadata=metadata or {},
            ip_address=ip_address,
        )
    except Exception as exc:  # noqa: BLE001
        # Never let audit logging break the main flow
        logger.exception("audit log_action failed: %s", exc)


def _get_client_ip(request) -> str | None:
    """Extract the real client IP from the request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")
