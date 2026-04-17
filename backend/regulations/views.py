import threading

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes

from .models import Regulation
from .serializers import (
    RegulationSerializer,
    RegulationListSerializer,
    RegulationUploadSerializer,
    RegulationStatusUpdateSerializer,
)
from .services import run_compliance_pipeline, extract_text_from_pdf
from audit.utils import log_action
from common.permissions import IsAdminRole, IsOrgMember


class RegulationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: RegulationListSerializer(many=True)},
        description="List all regulations belonging to the current user's organization.",
        parameters=[
            OpenApiParameter("region", str, description="Filter by region"),
            OpenApiParameter("industry", str, description="Filter by industry"),
            OpenApiParameter(
                "status",
                str,
                description="Filter by status: new | updated | archived",
            ),
            OpenApiParameter(
                "pipeline_status",
                str,
                description="Filter by pipeline_status: pending | processing | completed | failed",
            ),
        ],
        tags=["Regulations"],
    )
    def get(self, request):
        qs = Regulation.objects.filter(organization=request.user.organization)

        region = request.query_params.get("region")
        industry = request.query_params.get("industry")
        reg_status = request.query_params.get("status")
        pipeline_status = request.query_params.get("pipeline_status")

        if region:
            qs = qs.filter(region__icontains=region)
        if industry:
            qs = qs.filter(industry__icontains=industry)
        if reg_status:
            qs = qs.filter(status=reg_status)
        if pipeline_status:
            qs = qs.filter(pipeline_status=pipeline_status)

        return Response(RegulationListSerializer(qs, many=True).data)

    @extend_schema(
        request=RegulationUploadSerializer,
        responses={201: RegulationSerializer},
        description=(
            "Upload a new regulation (PDF or raw text). "
            "Automatically triggers the full compliance pipeline: "
            "analyze → assess risk → generate tasks. "
            "Admin role required."
        ),
        tags=["Regulations"],
    )
    def post(self, request):
        # Only Admin can upload
        if not request.user.role or request.user.role.name.lower() != "admin":
            return Response(
                {"detail": "Only Admin users can upload regulations."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RegulationUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Extract text if PDF provided
        raw_text = data.get("raw_text", "")
        pdf_file = data.get("pdf_file")
        if pdf_file and not raw_text:
            raw_text = extract_text_from_pdf(pdf_file)

        regulation = Regulation.objects.create(
            organization=request.user.organization,
            created_by=request.user,
            title=data["title"],
            source=data["source"],
            region=data["region"],
            industry=data["industry"],
            raw_text=raw_text,
            pdf_file=pdf_file,
            published_date=data.get("published_date"),
            effective_date=data.get("effective_date"),
            pipeline_status="pending",
        )

        log_action(
            user=request.user,
            action="regulation_created",
            entity_type="Regulation",
            entity_id=str(regulation.id),
            description=f"Regulation uploaded: {regulation.title}",
            organization=request.user.organization,
            request=request,
        )

        # Trigger pipeline in background thread
        pipeline_thread = threading.Thread(
            target=run_compliance_pipeline,
            args=(regulation, request.user),
            daemon=True,
        )
        pipeline_thread.start()

        return Response(
            RegulationSerializer(regulation).data,
            status=status.HTTP_201_CREATED,
        )


class RegulationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get_regulation(self, pk, user):
        try:
            return Regulation.objects.get(pk=pk, organization=user.organization)
        except Regulation.DoesNotExist:
            return None

    @extend_schema(
        responses={200: RegulationSerializer},
        description="Retrieve a single regulation's full details.",
        tags=["Regulations"],
    )
    def get(self, request, pk):
        regulation = self._get_regulation(pk, request.user)
        if not regulation:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(RegulationSerializer(regulation).data)

    @extend_schema(
        request=RegulationStatusUpdateSerializer,
        responses={200: RegulationSerializer},
        description="Update a regulation's status (new | updated | archived). Admin only.",
        tags=["Regulations"],
    )
    def patch(self, request, pk):
        if not request.user.role or request.user.role.name.lower() != "admin":
            return Response(
                {"detail": "Only Admin users can update regulations."},
                status=status.HTTP_403_FORBIDDEN,
            )
        regulation = self._get_regulation(pk, request.user)
        if not regulation:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RegulationStatusUpdateSerializer(regulation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        log_action(
            user=request.user,
            action="regulation_updated",
            entity_type="Regulation",
            entity_id=str(regulation.id),
            description=f"Regulation status updated: {regulation.title}",
            organization=request.user.organization,
            request=request,
        )
        return Response(RegulationSerializer(regulation).data)


class RegulationRetriggerPipelineView(APIView):
    """Re-run the compliance pipeline for a regulation that previously failed."""

    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    @extend_schema(
        responses={202: {"type": "object", "properties": {"detail": {"type": "string"}}}},
        description="Re-trigger the compliance pipeline for a failed regulation. Admin only.",
        tags=["Regulations"],
    )
    def post(self, request, pk):
        try:
            regulation = Regulation.objects.get(pk=pk, organization=request.user.organization)
        except Regulation.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if regulation.pipeline_status == "processing":
            return Response(
                {"detail": "Pipeline is already running."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        threading.Thread(
            target=run_compliance_pipeline,
            args=(regulation, request.user),
            daemon=True,
        ).start()

        return Response(
            {"detail": "Pipeline re-triggered."},
            status=status.HTTP_202_ACCEPTED,
        )
