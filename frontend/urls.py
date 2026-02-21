from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import (
    home,
    register_view,
    forgot_password_view,
    reset_password_view,
    read_view,
    favorites_view,
)

from .views_auth import OwlsightLoginView, owlsight_logout


urlpatterns = [
    # Página inicial
    path("", home, name="home"),

    # 🔐 LOGIN SEGURO (Class-Based View)
    path("login/", OwlsightLoginView.as_view(), name="login"),

    # Logout (POST only)
    path("logout/", owlsight_logout, name="logout"),

    # Registro e recuperação
    path("register/", register_view, name="register"),
    path("forgot-password/", forgot_password_view, name="forgot_password"),
    path("reset-password/", reset_password_view, name="reset_password"),

    # 🔒 PÁGINAS PROTEGIDAS (exigem login)
    path(
        "read/<int:book_id>/<int:page_number>/",
        login_required(read_view),
        name="read"
    ),

    path(
        "favorites/",
        login_required(favorites_view),
        name="favorites"
    ),
]