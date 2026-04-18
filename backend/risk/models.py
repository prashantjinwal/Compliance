import uuid
from django.db import models


RISK_LEVEL_CHOICES = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("critical", "Critical"),
]

RISK_STATUS_CHOICES = [
    ("open", "Open"),
    ("mitigated", "Mitigated"),
    ("accepted", "Accepted"),
]

RESPONSIBLE_ROLE_CHOICES = [
    ("legal", "Legal"),
    ("it", "IT"),
    ("finance", "Finance"),
    ("hr", "HR"),
    ("compliance", "Compliance"),
    ("admin", "Admin"),
]


class Risk(models.Model):
    """Stores the output of the AI assess_risk() call."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    regulation = models.ForeignKey(
        "regulations.Regulation",
        on_delete=models.CASCADE,
        related_name="risks",
    )
    analysis = models.OneToOneField(
        "analysis.Analysis",
        on_delete=models.CASCADE,
        related_name="risk",
    )
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="risks",
    )

    # AI output fields
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default="medium")
    impacted_area = models.CharField(max_length=255)
    description = models.TextField()
    responsible_role = models.CharField(
        max_length=50, choices=RESPONSIBLE_ROLE_CHOICES, default="compliance"
    )

    # User-managed
    status = models.CharField(max_length=20, choices=RISK_STATUS_CHOICES, default="open")
    mitigation_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_risk_level_display()} risk — {self.regulation.title}"
