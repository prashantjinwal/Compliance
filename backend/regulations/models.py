import uuid
from django.db import models
from django.conf import settings


class Regulation(models.Model):
    STATUS_CHOICES = (
        ("new", "New"),
        ("updated", "Updated"),
        ("archived", "Archived"),
    )

    PIPELINE_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Ownership
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="regulations",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_regulations",
    )

    # Content
    title = models.CharField(max_length=500)
    source = models.CharField(max_length=255, help_text="e.g. RBI, SEC, EU Commission")
    region = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)
    raw_text = models.TextField()
    pdf_file = models.FileField(upload_to="regulations/pdfs/", null=True, blank=True)

    # Dates
    published_date = models.DateField(null=True, blank=True)
    effective_date = models.DateField(null=True, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    pipeline_status = models.CharField(
        max_length=20, choices=PIPELINE_STATUS_CHOICES, default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
