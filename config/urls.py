from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def health(request):
    return HttpResponse("Owlsight está online ✅")

urlpatterns = [
    path("admin/", admin.site.urls),

    # ✅ API Auth (csrf / me / login / logout)
    path("api/", include("frontend.api_urls")),

    # ✅ API Books: /api/books/
    path("api/", include("books.urls")),

    # ✅ Dashboard
    path("dash/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),

    # ✅ Frontend (templates)
    path("", include("frontend.urls")),

    path("health/", health),

    path("api/", include("reading.urls")),
]