from django.urls import path
from . import api_views

urlpatterns = [
    path("csrf/", api_views.csrf, name="api-csrf"),

    path("auth/me/", api_views.me, name="api-me"),
    path("auth/login/", api_views.login_view, name="api-login"),
    path("auth/logout/", api_views.logout_view, name="api-logout"),
]