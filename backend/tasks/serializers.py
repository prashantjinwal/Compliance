from rest_framework import serializers
from .models import ComplianceTask


class ComplianceTaskSerializer(serializers.ModelSerializer):
    regulation_title = serializers.CharField(source="regulation.title", read_only=True)
    assigned_to_name = serializers.CharField(
        source="assigned_to.full_name", read_only=True, default=None
    )
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceTask
        fields = [
            "id", "regulation_id", "regulation_title",
            "risk_id",
            "title", "description", "suggested_action",
            "deadline", "assigned_role",
            "assigned_to", "assigned_to_name",
            "status", "notes", "completed_at",
            "is_overdue",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "regulation_id", "regulation_title", "risk_id",
            "title", "description", "suggested_action",
            "completed_at", "is_overdue",
            "created_at", "updated_at",
        ]

    def get_is_overdue(self, obj) -> bool:
        from datetime import date
        if obj.deadline and obj.status not in ("completed",):
            return obj.deadline < date.today()
        return False


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    """PATCH — update status, notes, assignment."""
    class Meta:
        model = ComplianceTask
        fields = ["status", "notes", "assigned_to", "assigned_role", "deadline"]

    def validate_status(self, value):
        allowed = [c[0] for c in ComplianceTask._meta.get_field("status").choices]
        if value not in allowed:
            raise serializers.ValidationError(f"Status must be one of: {allowed}")
        return value

    def update(self, instance, validated_data):
        from django.utils import timezone
        if validated_data.get("status") == "completed" and instance.status != "completed":
            validated_data["completed_at"] = timezone.now()
        return super().update(instance, validated_data)


class DashboardTaskSerializer(serializers.ModelSerializer):
    """Minimal task summary for the dashboard widget."""
    regulation_title = serializers.CharField(source="regulation.title", read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceTask
        fields = [
            "id", "title", "assigned_role", "status",
            "deadline", "is_overdue", "regulation_title",
        ]

    def get_is_overdue(self, obj) -> bool:
        from datetime import date
        if obj.deadline and obj.status not in ("completed",):
            return obj.deadline < date.today()
        return False
