from rest_framework import serializers
from .models import ChatMessage

# uploaded document or text related serializers

class UploadDocumentSerializer(serializers.Serializer):
    file = serializers.FileField(required=False)
    text = serializers.CharField(required=False)

    def validate(self, data):
        if not data.get("file") and not data.get("text"):
            raise serializers.ValidationError("Provide either file or text")
        return data


class UploadResponseSerializer(serializers.Serializer):
    doc_id = serializers.UUIDField()
    summary = serializers.CharField()


class ChatWithDocSerializer(serializers.Serializer):
    question = serializers.CharField()
    session_id = serializers.UUIDField(required=False)



class ChatResponseSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    answer = serializers.CharField()

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "role", "content", "created_at"]
