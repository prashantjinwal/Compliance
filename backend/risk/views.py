from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Risk
from .serializers import RiskSerializer, RiskStatusUpdateSerializer
from audit.utils import log_action


class RiskListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: RiskSerializer(many=True)},
        description="List risks for the current organization.",
        parameters=[
            OpenApiParameter("risk_level", str, description="Filter: low | medium | high | critical"),
            OpenApiParameter("status", str, description="Filter: open | mitigated | accepted"),
        ],
        tags=["Risk"],
    )
    def get(self, request):
        qs = Risk.objects.filter(organization=request.user.organization).select_related(
            "regulation"
        )
        risk_level = request.query_params.get("risk_level")
        risk_status = request.query_params.get("status")

        if risk_level:
            qs = qs.filter(risk_level=risk_level)
        if risk_status:
            qs = qs.filter(status=risk_status)

        return Response(RiskSerializer(qs, many=True).data)


class RiskDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get_risk(self, pk, user):
        try:
            return Risk.objects.get(pk=pk, organization=user.organization)
        except Risk.DoesNotExist:
            return None

    @extend_schema(
        responses={200: RiskSerializer},
        description="Get a risk record by ID.",
        tags=["Risk"],
    )
    def get(self, request, pk):
        risk = self._get_risk(pk, request.user)
        if not risk:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(RiskSerializer(risk).data)

    @extend_schema(
        request=RiskStatusUpdateSerializer,
        responses={200: RiskSerializer},
        description="Update a risk's status or mitigation notes.",
        tags=["Risk"],
    )
    def patch(self, request, pk):
        risk = self._get_risk(pk, request.user)
        if not risk:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RiskStatusUpdateSerializer(risk, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        log_action(
            user=request.user,
            action="risk_status_updated",
            entity_type="Risk",
            entity_id=str(risk.id),
            description=f"Risk status updated to '{risk.status}': {risk.regulation.title}",
            organization=request.user.organization,
            request=request,
        )
        return Response(RiskSerializer(risk).data)


class RegulationRisksView(APIView):
    """GET /api/regulations/<regulation_id>/risks/ — risks for a specific regulation."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: RiskSerializer(many=True)},
        description="Get all risks linked to a specific regulation.",
        tags=["Risk"],
    )
    def get(self, request, regulation_id):
        qs = Risk.objects.filter(
            regulation_id=regulation_id,
            organization=request.user.organization,
        ).select_related("regulation")
        return Response(RiskSerializer(qs, many=True).data)
