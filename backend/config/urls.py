from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),

    # ── Auth & Accounts ───────────────────────────────────────────────────────
    path("api/auth/", include("accounts.urls")),

    # ── Compliance Pipeline ───────────────────────────────────────────────────
    path("api/regulations/", include("regulations.urls")),
    path("api/analysis/", include("analysis.urls")),
    path("api/risks/", include("risk.urls")),
    path("api/tasks/", include("tasks.urls")),


    # ── Reporting & Audit ─────────────────────────────────────────────────────
    path("api/reports/", include("reports.urls")),
    path("api/audit/", include("audit.urls")),

    # ── Copilot (existing RAG chat) ───────────────────────────────────────────
    path("api/copilot/", include("copilot.urls")),

    # ── API Docs ──────────────────────────────────────────────────────────────
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
