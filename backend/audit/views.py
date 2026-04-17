from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import AuditLog
from .serializers import AuditLogSerializer
from common.permissions import IsAuditorRole


class AuditLogListView(APIView):
    """
    GET /api/audit/logs/

    Returns the full audit trail for the organization.
    Filterable by action, entity_type, entity_id.
    Accessible by Admin and Auditor roles only.
    """

    permission_classes = [permissions.IsAuthenticated, IsAuditorRole]

    @extend_schema(
        responses={200: AuditLogSerializer(many=True)},
        description=(
            "List all audit log entries for the organization. "
            "Supports filtering by action, entity_type, entity_id, and date range. "
            "Admin and Auditor roles only."
        ),
        parameters=[
            OpenApiParameter("action", str, description="Filter by action key (e.g. task_created)"),
            OpenApiParameter("entity_type", str, description="Filter by entity type (e.g. Regulation)"),
            OpenApiParameter("entity_id", str, description="Filter by entity UUID"),
            OpenApiParameter("date_from", str, description="ISO date — start of range (YYYY-MM-DD)"),
            OpenApiParameter("date_to", str, description="ISO date — end of range (YYYY-MM-DD)"),
        ],
        tags=["Audit"],
    )
    def get(self, request):
        qs = AuditLog.objects.filter(organization=request.user.organization)

        action = request.query_params.get("action")
        entity_type = request.query_params.get("entity_type")
        entity_id = request.query_params.get("entity_id")
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")

        if action:
            qs = qs.filter(action=action)
        if entity_type:
            qs = qs.filter(entity_type__iexact=entity_type)
        if entity_id:
            qs = qs.filter(entity_id=entity_id)
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        return Response(AuditLogSerializer(qs, many=True).data)


class AuditLogDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAuditorRole]

    @extend_schema(
        responses={200: AuditLogSerializer},
        description="Retrieve a single audit log entry.",
        tags=["Audit"],
    )
    def get(self, request, pk):
        try:
            log = AuditLog.objects.get(pk=pk, organization=request.user.organization)
        except AuditLog.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(AuditLogSerializer(log).data)


class AuditTimelineView(APIView):
    """
    GET /api/audit/timeline/<entity_type>/<entity_id>/

    Returns a chronological audit trail for a specific entity.
    Useful for viewing the full history of a regulation, task, or risk.
    """

    permission_classes = [permissions.IsAuthenticated, IsAuditorRole]

    @extend_schema(
        responses={200: AuditLogSerializer(many=True)},
        description=(
            "Chronological audit timeline for a specific entity. "
            "Use this to trace the full history of any regulation, task, risk, or report."
        ),
        tags=["Audit"],
    )
    def get(self, request, entity_type, entity_id):
        qs = AuditLog.objects.filter(
            organization=request.user.organization,
            entity_type__iexact=entity_type,
            entity_id=str(entity_id),
        )
        return Response(AuditLogSerializer(qs, many=True).data)


class AuditExportView(APIView):
    """
    GET /api/audit/export/

    Returns the complete audit package as a flat list of all logs
    (used by the frontend to build the downloadable PDF audit bundle).
    """

    permission_classes = [permissions.IsAuthenticated, IsAuditorRole]

    @extend_schema(
        responses={200: AuditLogSerializer(many=True)},
        description=(
            "Export the full organization audit log. "
            "Use this endpoint to fetch data for generating the audit PDF bundle. "
            "Returns all logs chronologically."
        ),
        tags=["Audit"],
    )
    def get(self, request):
        qs = AuditLog.objects.filter(
            organization=request.user.organization
        ).order_by("created_at")
        return Response(AuditLogSerializer(qs, many=True).data)
