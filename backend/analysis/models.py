import uuid
from django.db import models


class Analysis(models.Model):
    """Stores the output of the AI analyze_regulation() call."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    regulation = models.OneToOneField(
        "regulations.Regulation",
        on_delete=models.CASCADE,
        related_name="analysis",
    )
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="analyses",
    )

    # AI output fields
    summary = models.TextField()
    key_changes = models.TextField(blank=True)
    obligations = models.JSONField(default=list)   # list of obligation strings
    relevance_score = models.FloatField(default=0.0)  # 0.0 – 1.0

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "analyses"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Analysis for {self.regulation.title}"
