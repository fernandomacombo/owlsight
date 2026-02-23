from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def health(request):
    return HttpResponse("Owlsight está online ✅")

urlpatterns = [
    path("admin/", admin.site.urls),

    # ✅ API (tudo aqui dentro)
    path("api/", include("frontend.api_urls")),  # csrf/me/login/logout
    path("api/", include("books.urls")),         # /api/books/...
    path("api/", include("reading.urls")),       # /api/read/<book>/<page>/  ✅ (vamos criar já abaixo)

    # ✅ Dashboard
    path("dash/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),

    # ✅ Frontend (templates)
    path("", include("frontend.urls")),

    path("health/", health),
]