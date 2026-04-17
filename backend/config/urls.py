from django.contrib import admin
from django.urls import path, include

try:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
except ImportError:
    SpectacularAPIView = None
    SpectacularSwaggerView = None

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
]

if SpectacularAPIView and SpectacularSwaggerView:
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    ]
