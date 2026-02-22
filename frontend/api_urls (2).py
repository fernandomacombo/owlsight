from django.urls import path
from . import api_auth

urlpatterns = [
    path("csrf/", api_auth.csrf),
    path("auth/me/", api_auth.me),
    path("auth/login/", api_auth.login_view),
    path("auth/logout/", api_auth.logout_view),
]