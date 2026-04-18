from rest_framework import serializers


class AITextAnalysisSerializer(serializers.Serializer):
    text = serializers.CharField(required=False, allow_blank=True)


class AIQuerySerializer(serializers.Serializer):
    message = serializers.CharField()

