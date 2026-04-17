from rest_framework import serializers
from .models import ComplianceReport


class ComplianceReportSerializer(serializers.ModelSerializer):
    generated_by_name = serializers.CharField(
        source="generated_by.full_name", read_only=True, default=""
    )
    regulation_ids = serializers.PrimaryKeyRelatedField(
        source="regulations",
        many=True,
        read_only=True,
    )

    class Meta:
        model = ComplianceReport
        fields = [
            "id", "title", "generated_by_name", "regulation_ids",
            "summary", "risks_summary", "actions_taken", "pending_issues",
            "compliance_status", "status", "report_file",
            "created_at", "updated_at",
        ]
        read_only_fields = fields


class GenerateReportInputSerializer(serializers.Serializer):
    """POST /api/reports/generate/ — specify which regulations to include."""
    title = serializers.CharField(max_length=255)
    regulation_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of regulation UUIDs to include in the report.",
    )
