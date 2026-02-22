from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def health(request):
    return HttpResponse("Owlsight está online ✅")

urlpatterns = [
    # Admin Django
    path("admin/", admin.site.urls),

    # ✅ API Auth (csrf / me / login / logout)
    path("api/", include("frontend.api_urls")),

    # ✅ API Books (ATENÇÃO: deixa só UMA forma)
    # Se em books/urls.py tu definiste o endpoint como "books/",
    # então aqui fica "api/" e lá dentro fica "books/".
    path("api/", include("books.urls")),

    # Dashboard
    path("dash/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),

    # Frontend (templates)
    path("", include("frontend.urls")),

    # health check
    path("health/", health),
]