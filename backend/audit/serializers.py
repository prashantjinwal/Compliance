from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True, default="system")
    user_name = serializers.CharField(source="user.full_name", read_only=True, default="System")
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id", "action", "action_display",
            "entity_type", "entity_id",
            "description", "metadata",
            "user_email", "user_name",
            "ip_address", "created_at",
        ]
        read_only_fields = fields
