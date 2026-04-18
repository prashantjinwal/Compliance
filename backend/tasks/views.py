from datetime import date

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import ComplianceTask
from .serializers import (
    ComplianceTaskSerializer,
    TaskStatusUpdateSerializer,
    DashboardTaskSerializer,
)
from audit.utils import log_action


class TaskListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: ComplianceTaskSerializer(many=True)},
        description=(
            "List compliance tasks for the current organization. "
            "Supports filtering by role, status, and overdue flag."
        ),
        parameters=[
            OpenApiParameter("assigned_role", str, description="Filter by role: Legal | IT | Finance | HR | Compliance | Admin"),
            OpenApiParameter("status", str, description="Filter by status: pending | in_progress | completed | blocked"),
            OpenApiParameter("overdue", str, description="Pass 'true' to list only overdue tasks"),
            OpenApiParameter("regulation_id", str, description="Filter tasks for a specific regulation UUID"),
        ],
        tags=["Tasks"],
    )
    def get(self, request):
        qs = ComplianceTask.objects.filter(
            organization=request.user.organization
        ).select_related("regulation", "assigned_to", "risk")

        # Role filter — users can narrow to their own role bucket
        assigned_role = request.query_params.get("assigned_role")
        task_status = request.query_params.get("status")
        overdue = request.query_params.get("overdue", "").lower() == "true"
        regulation_id = request.query_params.get("regulation_id")

        if assigned_role:
            qs = qs.filter(assigned_role__iexact=assigned_role)
        if task_status:
            qs = qs.filter(status=task_status)
        if overdue:
            qs = qs.filter(deadline__lt=date.today()).exclude(status="completed")
        if regulation_id:
            qs = qs.filter(regulation_id=regulation_id)

        return Response(ComplianceTaskSerializer(qs, many=True).data)


class TaskDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get_task(self, pk, user):
        try:
            return ComplianceTask.objects.get(pk=pk, organization=user.organization)
        except ComplianceTask.DoesNotExist:
            return None

    @extend_schema(
        responses={200: ComplianceTaskSerializer},
        description="Retrieve a compliance task's full details.",
        tags=["Tasks"],
    )
    def get(self, request, pk):
        task = self._get_task(pk, request.user)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ComplianceTaskSerializer(task).data)

    @extend_schema(
        request=TaskStatusUpdateSerializer,
        responses={200: ComplianceTaskSerializer},
        description=(
            "Update task status, notes, assignment, or deadline. "
            "Setting status to 'completed' automatically records completed_at."
        ),
        tags=["Tasks"],
    )
    def patch(self, request, pk):
        task = self._get_task(pk, request.user)
        if not task:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        old_status = task.status
        serializer = TaskStatusUpdateSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        new_status = task.status
        action = "task_completed" if new_status == "completed" else "task_updated"

        log_action(
            user=request.user,
            action=action,
            entity_type="ComplianceTask",
            entity_id=str(task.id),
            description=f"Task '{task.title}' updated: {old_status} → {new_status}",
            organization=request.user.organization,
            metadata={"old_status": old_status, "new_status": new_status},
            request=request,
        )
        return Response(ComplianceTaskSerializer(task).data)


class DashboardView(APIView):
    """
    GET /api/tasks/dashboard/

    Returns an aggregated dashboard payload:
    - tasks grouped by role
    - overdue tasks
    - open risks count
    - task status summary
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={
            200: {
                "type": "object",
                "properties": {
                    "total_tasks": {"type": "integer"},
                    "by_status": {"type": "object"},
                    "by_role": {"type": "object"},
                    "overdue_tasks": {"type": "array"},
                    "upcoming_tasks": {"type": "array"},
                    "open_risks": {"type": "integer"},
                    "new_regulations": {"type": "integer"},
                },
            }
        },
        description="Dashboard summary — tasks by role/status, overdue list, risk counts.",
        tags=["Dashboard"],
    )
    def get(self, request):
        from risk.models import Risk
        from regulations.models import Regulation
        from django.utils import timezone
        from datetime import timedelta

        org = request.user.organization
        today = date.today()
        next_week = today + timedelta(days=7)

        tasks = ComplianceTask.objects.filter(organization=org)

        # Status breakdown
        status_counts = {}
        for choice_key, _ in ComplianceTask._meta.get_field("status").choices:
            status_counts[choice_key] = tasks.filter(status=choice_key).count()

        # Role breakdown
        role_counts = {}
        for t in tasks:
            role_counts[t.assigned_role] = role_counts.get(t.assigned_role, 0) + 1

        # Overdue
        overdue = tasks.filter(deadline__lt=today).exclude(status="completed")

        # Upcoming (due within 7 days, not completed)
        upcoming = tasks.filter(
            deadline__gte=today, deadline__lte=next_week
        ).exclude(status="completed")

        # Open risk count
        open_risks = Risk.objects.filter(organization=org, status="open").count()

        # New regulations (last 7 days)
        new_regs = Regulation.objects.filter(
            organization=org,
            created_at__gte=timezone.now() - timedelta(days=7),
        ).count()

        return Response({
            "total_tasks": tasks.count(),
            "by_status": status_counts,
            "by_role": role_counts,
            "overdue_tasks": DashboardTaskSerializer(overdue[:10], many=True).data,
            "upcoming_tasks": DashboardTaskSerializer(upcoming[:10], many=True).data,
            "open_risks": open_risks,
            "new_regulations": new_regs,
        })
