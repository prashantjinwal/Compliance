from rest_framework import serializers
from .models import Analysis


class AnalysisSerializer(serializers.ModelSerializer):
    regulation_title = serializers.CharField(source="regulation.title", read_only=True)
    regulation_id = serializers.UUIDField(source="regulation.id", read_only=True)

    class Meta:
        model = Analysis
        fields = [
            "id", "regulation_id", "regulation_title",
            "summary", "key_changes", "obligations", "relevance_score",
            "created_at", "updated_at",
        ]
        read_only_fields = fields
