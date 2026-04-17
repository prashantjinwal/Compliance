from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema

from .models import ComplianceReport
from .serializers import ComplianceReportSerializer, GenerateReportInputSerializer
from audit.utils import log_action


class ReportListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: ComplianceReportSerializer(many=True)},
        description="List all compliance reports for the current organization.",
        tags=["Reports"],
    )
    def get(self, request):
        qs = ComplianceReport.objects.filter(organization=request.user.organization)
        return Response(ComplianceReportSerializer(qs, many=True).data)


class GenerateReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=GenerateReportInputSerializer,
        responses={201: ComplianceReportSerializer},
        description=(
            "Generate a compliance report for the specified regulations. "
            "Aggregates risk counts, task completion data, and pending issues."
        ),
        tags=["Reports"],
    )
    def post(self, request):
        serializer = GenerateReportInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        title = serializer.validated_data["title"]
        regulation_ids = serializer.validated_data["regulation_ids"]

        from regulations.models import Regulation
        from risk.models import Risk
        from tasks.models import ComplianceTask

        regulations = Regulation.objects.filter(
            id__in=regulation_ids,
            organization=request.user.organization,
        )
        if not regulations.exists():
            return Response(
                {"detail": "No matching regulations found for your organization."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Aggregate data ────────────────────────────────────────────────────
        reg_ids = list(regulations.values_list("id", flat=True))
        risks = Risk.objects.filter(regulation_id__in=reg_ids)
        tasks = ComplianceTask.objects.filter(regulation_id__in=reg_ids)

        risks_summary = {
            "total": risks.count(),
            "critical": risks.filter(risk_level="critical").count(),
            "high": risks.filter(risk_level="high").count(),
            "medium": risks.filter(risk_level="medium").count(),
            "low": risks.filter(risk_level="low").count(),
            "open": risks.filter(status="open").count(),
            "mitigated": risks.filter(status="mitigated").count(),
        }

        actions_taken = list(
            tasks.filter(status="completed").values(
                "id", "title", "assigned_role", "completed_at"
            )
        )
        # Serialize UUIDs and dates
        for item in actions_taken:
            item["id"] = str(item["id"])
            if item["completed_at"]:
                item["completed_at"] = item["completed_at"].isoformat()

        pending_issues = list(
            tasks.exclude(status="completed").values(
                "id", "title", "assigned_role", "deadline", "status"
            )
        )
        for item in pending_issues:
            item["id"] = str(item["id"])
            if item["deadline"]:
                item["deadline"] = item["deadline"].isoformat()

        # Determine overall compliance status
        if risks.filter(risk_level__in=["critical", "high"], status="open").exists():
            compliance_status = "non_compliant"
        elif risks.filter(status="open").exists():
            compliance_status = "partial"
        else:
            compliance_status = "compliant"

        summary = (
            f"Compliance report covering {regulations.count()} regulation(s). "
            f"Total risks: {risks_summary['total']}, "
            f"Open: {risks_summary['open']}, "
            f"Tasks completed: {len(actions_taken)}, "
            f"Pending: {len(pending_issues)}."
        )

        report = ComplianceReport.objects.create(
            organization=request.user.organization,
            generated_by=request.user,
            title=title,
            summary=summary,
            risks_summary=risks_summary,
            actions_taken=actions_taken,
            pending_issues=pending_issues,
            compliance_status=compliance_status,
            status="draft",
        )
        report.regulations.set(regulations)

        log_action(
            user=request.user,
            action="report_generated",
            entity_type="ComplianceReport",
            entity_id=str(report.id),
            description=f"Report generated: {title}",
            organization=request.user.organization,
            metadata={"regulation_count": regulations.count()},
            request=request,
        )
        return Response(
            ComplianceReportSerializer(report).data, status=status.HTTP_201_CREATED
        )


class ReportDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: ComplianceReportSerializer},
        description="Retrieve a single compliance report.",
        tags=["Reports"],
    )
    def get(self, request, pk):
        try:
            report = ComplianceReport.objects.get(pk=pk, organization=request.user.organization)
        except ComplianceReport.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ComplianceReportSerializer(report).data)
