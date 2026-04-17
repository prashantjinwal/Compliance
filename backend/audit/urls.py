from django.urls import path
from .views import AuditLogListView, AuditLogDetailView, AuditTimelineView, AuditExportView

urlpatterns = [
    path("logs/", AuditLogListView.as_view(), name="audit-log-list"),
    path("logs/<uuid:pk>/", AuditLogDetailView.as_view(), name="audit-log-detail"),
    path("timeline/<str:entity_type>/<str:entity_id>/", AuditTimelineView.as_view(), name="audit-timeline"),
    path("export/", AuditExportView.as_view(), name="audit-export"),
]
