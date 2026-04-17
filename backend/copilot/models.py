# copilot/models.py

import uuid
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class UserDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")

    title = models.CharField(max_length=255, blank=True)

    file = models.FileField(upload_to="user_docs/")
    raw_text = models.TextField()

    summary = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or str(self.id)




class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    document = models.ForeignKey(
        UserDocument,
        on_delete=models.CASCADE,
        related_name="chat_sessions"
    )

    created_at = models.DateTimeField(auto_now_add=True)


class ChatMessage(models.Model):
    ROLE_CHOICES = (
        ("user", "User"),
        ("assistant", "Assistant"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
