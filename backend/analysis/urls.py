from django.urls import path
from .views import AnalysisListView, AnalysisDetailView

urlpatterns = [
    path("", AnalysisListView.as_view(), name="analysis-list"),
    path("<uuid:pk>/", AnalysisDetailView.as_view(), name="analysis-detail"),
]
