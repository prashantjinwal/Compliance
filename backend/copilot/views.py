from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


from .serializers import ChatResponseSerializer, UploadDocumentSerializer, UploadResponseSerializer , ChatResponseSerializer , ChatWithDocSerializer
from .models import UserDocument , ChatMessage , ChatSession
from drf_spectacular.utils import extend_schema

from .utils import extract_text_from_pdf
from .rag.vector_store import create_vector_store
from .rag.pipeline import summarize_document , chat_with_doc


class UploadAndSummarizeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=UploadDocumentSerializer,
        responses=UploadResponseSerializer,
        description="Upload a PDF or text and get summarized output"
    )
    def post(self, request):
        serializer = UploadDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data.get("file")
        text_input = serializer.validated_data.get("text")

        if file:
            raw_text = extract_text_from_pdf(file)
        else:
            raw_text = text_input

        doc = UserDocument.objects.create(
            user=request.user,
            file=file if file else None,
            raw_text=raw_text
        )

        create_vector_store(doc.id, raw_text)

        summary = summarize_document(raw_text)

        return Response({
            "doc_id": str(doc.id),
            "summary": summary
        })


class ChatWithDocView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ChatWithDocSerializer,
        responses=ChatResponseSerializer,
        description="Chat with document and store messages"
    )
    def post(self, request, doc_id):
        serializer = ChatWithDocSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data["question"]
        session_id = serializer.validated_data.get("session_id")

        # 🔹 Get or create session
        if session_id:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(
                user=request.user,
                document_id=doc_id
            )

        # 🔹 Save user message
        ChatMessage.objects.create(
            session=session,
            role="user",
            content=question
        )

        # 🔹 Get AI response
        answer = chat_with_doc(doc_id, question)

        # 🔹 Save AI message
        ChatMessage.objects.create(
            session=session,
            role="assistant",
            content=answer
        )

        return Response({
            "session_id": str(session.id),
            "answer": answer
        })
