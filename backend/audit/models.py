import uuid
from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    """
    Immutable audit trail of every significant compliance event.
    Records are written automatically via audit.utils.log_action().
    """

    ACTION_CHOICES = [
        ("regulation_created", "Regulation Created"),
        ("regulation_updated", "Regulation Updated"),
        ("analysis_generated", "Analysis Generated"),
        ("risk_assessed", "Risk Assessed"),
        ("task_created", "Task Created"),
        ("task_updated", "Task Updated"),
        ("task_completed", "Task Completed"),
        ("report_generated", "Report Generated"),
        ("note_added", "Note Added"),
        ("note_updated", "Note Updated"),
        ("risk_status_updated", "Risk Status Updated"),
        ("user_login", "User Login"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="audit_logs",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    entity_type = models.CharField(max_length=100, db_index=True)
    entity_id = models.CharField(max_length=100, db_index=True)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        # Audit logs are append-only — no update or delete in normal flow
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        return f"[{self.action}] {self.entity_type}:{self.entity_id}"
