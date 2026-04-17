from django.urls import path
from .views import RegisterView, LoginView, MeView, OrganizationDetailView, RoleListView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("organization/", OrganizationDetailView.as_view(), name="auth-organization"),
    path("roles/", RoleListView.as_view(), name="auth-roles"),
]
