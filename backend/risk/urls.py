from django.urls import path
from .views import RiskListView, RiskDetailView

urlpatterns = [
    path("", RiskListView.as_view(), name="risk-list"),
    path("<uuid:pk>/", RiskDetailView.as_view(), name="risk-detail"),
]
