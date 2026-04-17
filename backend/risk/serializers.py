from rest_framework import serializers
from .models import Risk


class RiskSerializer(serializers.ModelSerializer):
    regulation_title = serializers.CharField(source="regulation.title", read_only=True)
    regulation_id = serializers.UUIDField(source="regulation.id", read_only=True)

    class Meta:
        model = Risk
        fields = [
            "id", "regulation_id", "regulation_title",
            "risk_level", "impacted_area", "description", "responsible_role",
            "status", "mitigation_notes",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "regulation_id", "regulation_title",
            "risk_level", "impacted_area", "description", "responsible_role",
            "created_at", "updated_at",
        ]


class RiskStatusUpdateSerializer(serializers.ModelSerializer):
    """Allows users to update risk status and add mitigation notes."""
    class Meta:
        model = Risk
        fields = ["status", "mitigation_notes", "responsible_role"]
