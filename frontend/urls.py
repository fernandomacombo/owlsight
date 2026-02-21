from django.urls import path
from .views import (
    home,
    login_view,
    register_view,
    forgot_password_view,
    reset_password_view,
    read_view,
    favorites_view,
)

urlpatterns = [
    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("forgot-password/", forgot_password_view, name="forgot-password"),
    path("reset-password/", reset_password_view, name="reset-password"),
    path("read/<int:book_id>/<int:page_number>/", read_view, name="read"),
    path("favorites/", favorites_view, name="favorites"),
]