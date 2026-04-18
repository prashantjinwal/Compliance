from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .ai_service import analyze_text, analyze_uploaded_file, answer_query
from .serializers import AIQuerySerializer, AITextAnalysisSerializer


class AIAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        uploaded_file = request.FILES.get("file")
        serializer = None

        if uploaded_file is None:
            serializer = AITextAnalysisSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

        try:
            if uploaded_file is not None:
                return Response(analyze_uploaded_file(uploaded_file))

            text = serializer.validated_data.get("text", "").strip()

            if not text:
                raise ValidationError({"detail": "Provide either a file or text for analysis."})

            return Response(analyze_text(text))
        except ValidationError:
            raise
        except RuntimeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AIQueryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AIQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            return Response(answer_query(serializer.validated_data["message"]))
        except RuntimeError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
