from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from ai_services import analyze_regulation, assess_risk, generate_tasks

from .models import ChatMessage, ChatSession, UserDocument
from .rag.config import CopilotConfigurationError
from .rag.errors import CopilotRateLimitError
from .rag.pipeline import chat_with_doc, summarize_document
from .rag.vector_store import create_vector_store
from .serializers import (
    ChatResponseSerializer,
    ChatWithDocSerializer,
    UploadDocumentSerializer,
    UploadResponseSerializer,
)
from .utils import extract_text_from_pdf


def build_rate_limit_response(exc):
    payload = {
        "success": False,
        "error_code": exc.error_code,
        "error": "AI quota exceeded. Please retry in a few seconds.",
    }

    if exc.retry_seconds:
        payload["retry_seconds"] = exc.retry_seconds
        payload["error"] = f"AI quota exceeded. Please retry in about {exc.retry_seconds} seconds."

    response = Response(payload, status=status.HTTP_429_TOO_MANY_REQUESTS)

    if exc.retry_seconds:
        response["Retry-After"] = str(exc.retry_seconds)

    return response


class UploadAndSummarizeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=UploadDocumentSerializer,
        responses=UploadResponseSerializer,
        description="Upload a PDF or text and get summarized output",
    )
    def post(self, request):
        serializer = UploadDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data.get("file")
        text_input = serializer.validated_data.get("text")

        if file:
            raw_text = extract_text_from_pdf(file)
            title = file.name
        else:
            raw_text = text_input
            title = "Ad hoc text"

        try:
            summary = summarize_document(raw_text)
            analysis = analyze_regulation(raw_text)
            risk = assess_risk(analysis)
            tasks = generate_tasks(
                {
                    **risk,
                    "regulation_title": title,
                }
            )

            doc = UserDocument.objects.create(
                user=request.user,
                title=title,
                file=file if file else None,
                raw_text=raw_text,
                summary=summary,
            )

            create_vector_store(doc.id, raw_text)
        except CopilotConfigurationError as exc:
            return Response(
                {"success": False, "error_code": "CONFIGURATION_ERROR", "error": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except CopilotRateLimitError as exc:
            return build_rate_limit_response(exc)
        except Exception as exc:
            return Response(
                {
                    "success": False,
                    "error_code": "COPILOT_PROCESSING_FAILED",
                    "error": "Copilot processing failed. Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "success": True,
                "message": "File processed successfully",
                "data": {
                    "doc_id": str(doc.id),
                    "summary": summary,
                    "analysis": analysis,
                    "risk": risk,
                    "tasks": tasks,
                },
            }
        )


class ChatWithDocView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=ChatWithDocSerializer,
        responses=ChatResponseSerializer,
        description="Chat with document and store messages",
    )
    def post(self, request, doc_id):
        serializer = ChatWithDocSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data["question"]
        session_id = serializer.validated_data.get("session_id")

        try:
            document = UserDocument.objects.get(id=doc_id, user=request.user)
        except UserDocument.DoesNotExist:
            return Response(
                {"detail": "Document not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if session_id:
            try:
                session = ChatSession.objects.get(
                    id=session_id,
                    user=request.user,
                    document=document,
                )
            except ChatSession.DoesNotExist:
                return Response(
                    {"detail": "Chat session not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            session = ChatSession.objects.create(
                user=request.user,
                document=document,
            )

        ChatMessage.objects.create(
            session=session,
            role="user",
            content=question,
        )

        try:
            answer = chat_with_doc(doc_id, question)
        except CopilotConfigurationError as exc:
            return Response(
                {"success": False, "error_code": "CONFIGURATION_ERROR", "error": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except CopilotRateLimitError as exc:
            return build_rate_limit_response(exc)
        except Exception as exc:
            return Response(
                {
                    "success": False,
                    "error_code": "COPILOT_CHAT_FAILED",
                    "error": "Copilot chat failed. Please try again.",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        ChatMessage.objects.create(
            session=session,
            role="assistant",
            content=answer,
        )

        return Response(
            {
                "success": True,
                "message": "Chat response generated successfully",
                "data": {
                    "session_id": str(session.id),
                    "answer": answer,
                },
            }
        )
