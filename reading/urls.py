from django.urls import path
from . import api_views

urlpatterns = [
    path("progress/me/", api_views.progress_me, name="progress-me"),

    path("favorites/me/", api_views.favorites_me, name="favorites-me"),
    path("favorites/toggle/<int:book_id>/", api_views.favorites_toggle, name="favorites-toggle"),

    path("ratings/<int:book_id>/", api_views.rate_book, name="rate-book"),
]