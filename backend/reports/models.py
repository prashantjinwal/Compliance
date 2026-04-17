import uuid
from django.db import models
from django.conf import settings


REPORT_STATUS_CHOICES = [
    ("draft", "Draft"),
    ("final", "Final"),
]

COMPLIANCE_STATUS_CHOICES = [
    ("compliant", "Compliant"),
    ("partial", "Partial"),
    ("non_compliant", "Non-Compliant"),
    ("under_review", "Under Review"),
]


class ComplianceReport(models.Model):
    """
    Compliance report aggregating regulations, risks, and tasks for an organization.
    Generated on-demand; stored for audit readiness.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="reports",
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_reports",
    )

    title = models.CharField(max_length=255)

    # Scope
    regulations = models.ManyToManyField(
        "regulations.Regulation", blank=True, related_name="reports"
    )

    # Aggregated data (JSON snapshots at report-generation time)
    summary = models.TextField(blank=True)
    risks_summary = models.JSONField(default=dict)      # {total, high, medium, low}
    actions_taken = models.JSONField(default=list)      # [{task_id, title, status}]
    pending_issues = models.JSONField(default=list)     # [{task_id, title, deadline}]

    compliance_status = models.CharField(
        max_length=20, choices=COMPLIANCE_STATUS_CHOICES, default="under_review"
    )
    status = models.CharField(max_length=20, choices=REPORT_STATUS_CHOICES, default="draft")

    # Generated file
    report_file = models.FileField(upload_to="reports/files/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
