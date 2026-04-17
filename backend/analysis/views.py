from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema

from .models import Analysis
from .serializers import AnalysisSerializer


class AnalysisListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: AnalysisSerializer(many=True)},
        description="List all AI analyses for the current organization.",
        tags=["Analysis"],
    )
    def get(self, request):
        qs = Analysis.objects.filter(organization=request.user.organization).select_related(
            "regulation"
        )
        return Response(AnalysisSerializer(qs, many=True).data)


class AnalysisDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: AnalysisSerializer},
        description="Retrieve a specific analysis by ID.",
        tags=["Analysis"],
    )
    def get(self, request, pk):
        try:
            analysis = Analysis.objects.get(pk=pk, organization=request.user.organization)
        except Analysis.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(AnalysisSerializer(analysis).data)


class RegulationAnalysisView(APIView):
    """GET /api/regulations/<regulation_id>/analysis/ — analysis for a specific regulation."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: AnalysisSerializer},
        description="Get the AI analysis associated with a specific regulation.",
        tags=["Analysis"],
    )
    def get(self, request, regulation_id):
        try:
            analysis = Analysis.objects.get(
                regulation_id=regulation_id,
                organization=request.user.organization,
            )
        except Analysis.DoesNotExist:
            return Response(
                {"detail": "Analysis not found. Pipeline may still be running."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(AnalysisSerializer(analysis).data)
