from django.urls import path
from . import api_views
from . import views  # ✅ IMPORTA views (isto estava faltando)

urlpatterns = [
    path("progress/me/", api_views.progress_me, name="progress-me"),

    path("favorites/me/", api_views.favorites_me, name="favorites-me"),
    path("favorites/toggle/<int:book_id>/", api_views.favorites_toggle, name="favorites-toggle"),

    path("ratings/<int:book_id>/", api_views.rate_book, name="rate-book"),

    # ✅ LEITURA (o read.html chama isto)
    path("read/<int:book_id>/<int:page>/", views.read_page, name="api-read-page"),

    # ✅ desbloqueio por partilha (free)
    path("unlock/share/<int:book_id>/", views.unlock_share, name="api-unlock-share"),
]