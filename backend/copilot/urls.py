from django.urls import path
from .views import UploadAndSummarizeView, ChatWithDocView

urlpatterns = [
    path("upload/", UploadAndSummarizeView.as_view(), name="upload_and_summarize"),
    path("chat/<uuid:doc_id>/", ChatWithDocView.as_view(), name="chat_with_doc"),
]
