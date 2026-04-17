from django.urls import path
from .views import TaskListView, TaskDetailView, DashboardView

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="task-dashboard"),
    path("", TaskListView.as_view(), name="task-list"),
    path("<uuid:pk>/", TaskDetailView.as_view(), name="task-detail"),
]
