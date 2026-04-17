from django.urls import path, include
from .views import RegisterView, LoginView, MeView
from routers import routers

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("me/", MeView.as_view()),
    path("", include(routers.urls)),
]   
