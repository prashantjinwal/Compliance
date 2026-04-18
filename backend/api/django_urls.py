from django.urls import path

from .views import AIAnalyzeView, AIQueryView


urlpatterns = [
    path("analyze/", AIAnalyzeView.as_view()),
    path("analyze-regulation/", AIAnalyzeView.as_view()),
    path("chat/", AIQueryView.as_view()),
    path("query/", AIQueryView.as_view()),
]
