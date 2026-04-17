from django.urls import path
from .views import ReportListView, GenerateReportView, ReportDetailView

urlpatterns = [
    path("", ReportListView.as_view(), name="report-list"),
    path("generate/", GenerateReportView.as_view(), name="report-generate"),
    path("<uuid:pk>/", ReportDetailView.as_view(), name="report-detail"),
]
