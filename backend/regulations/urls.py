from django.urls import path
from .views import (
    RegulationListView,
    RegulationDetailView,
    RegulationRetriggerPipelineView,
)
from analysis.views import RegulationAnalysisView
from risk.views import RegulationRisksView

urlpatterns = [
    # Collection
    path("", RegulationListView.as_view(), name="regulation-list"),

    # Single item
    path("<uuid:pk>/", RegulationDetailView.as_view(), name="regulation-detail"),

    # Sub-resources scoped under a regulation
    path("<uuid:regulation_id>/analysis/", RegulationAnalysisView.as_view(), name="regulation-analysis"),
    path("<uuid:regulation_id>/risks/", RegulationRisksView.as_view(), name="regulation-risks"),

    # Pipeline management
    path("<uuid:pk>/retrigger/", RegulationRetriggerPipelineView.as_view(), name="regulation-retrigger"),
]
