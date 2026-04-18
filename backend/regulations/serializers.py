from rest_framework import serializers
from .models import Regulation


class RegulationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default="")

    class Meta:
        model = Regulation
        fields = [
            "id", "title", "source", "region", "industry",
            "status", "pipeline_status", "created_by_name",
            "published_date", "effective_date", "created_at",
        ]


class RegulationSerializer(serializers.ModelSerializer):
    """Full serializer for create/retrieve."""
    created_by_name = serializers.CharField(source="created_by.full_name", read_only=True, default="")
    organization_name = serializers.CharField(source="organization.name", read_only=True)

    class Meta:
        model = Regulation
        fields = [
            "id", "title", "source", "region", "industry",
            "raw_text", "pdf_file",
            "published_date", "effective_date",
            "status", "pipeline_status",
            "organization_name", "created_by_name",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "pipeline_status", "organization_name",
            "created_by_name", "created_at", "updated_at",
        ]


class RegulationUploadSerializer(serializers.Serializer):
    """Input for POST /api/regulations/ — supports both PDF and raw text."""
    title = serializers.CharField(max_length=500)
    source = serializers.CharField(max_length=255)
    region = serializers.CharField(max_length=100)
    industry = serializers.CharField(max_length=100)
    pdf_file = serializers.FileField(required=False, allow_null=True)
    raw_text = serializers.CharField(required=False, allow_blank=True)
    published_date = serializers.DateField(required=False, allow_null=True)
    effective_date = serializers.DateField(required=False, allow_null=True)

    def validate(self, data):
        if not data.get("pdf_file") and not data.get("raw_text"):
            raise serializers.ValidationError("Provide either pdf_file or raw_text.")
        return data


class RegulationStatusUpdateSerializer(serializers.ModelSerializer):
    """For PATCH /api/regulations/<id>/ — update status only."""
    class Meta:
        model = Regulation
        fields = ["status"]
