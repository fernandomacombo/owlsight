from django.urls import path
from .api_views import csrf_view, login_view, google_login_view

urlpatterns = [
    path("csrf/", csrf_view, name="api_csrf"),
    path("auth/login/", login_view, name="api_login"),
    path("auth/google/", google_login_view, name="api_google_login"),
]