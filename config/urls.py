from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def health(request):
    return HttpResponse("Owlsight está online ✅")

urlpatterns = [
    path("admin/", admin.site.urls),

    # ✅ APIs (mantém)
    path("api/books/", include("books.urls")),
    # Se tiveres outras APIs, adiciona aqui:
    # path("api/reading/", include("reading.urls")),
    # path("api/accounts/", include("accounts.urls")),

    # ✅ Frontend (templates)
    path("", include("frontend.urls")),

    # ✅ health check (opcional)
    path("health/", health),

     path("api/", include("frontend.api_urls")),

     path("dash/", include("dashboard.urls", namespace="dashboard")),

     path("api/", include("frontend.api_urls")),
]
