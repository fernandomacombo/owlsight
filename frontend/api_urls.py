from django.urls import path
from . import api_views
from . import api_auth


urlpatterns = [
    path("csrf/", api_views.csrf, name="api-csrf"),

    path("auth/me/", api_views.me, name="api-me"),
    path("auth/login/", api_views.login_view, name="api-login"),
    path("auth/logout/", api_views.logout_view, name="api-logout"),

    path("csrf/", api_auth.csrf),
    path("auth/me/", api_auth.me),
    path("auth/login/", api_auth.login_view),
    path("auth/logout/", api_auth.logout_view),
]