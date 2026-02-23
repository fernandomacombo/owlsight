from django.urls import path
from .views import RegisterAPIView, MeAPIView

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="auth_register"),
    path("me/", MeAPIView.as_view(), name="auth_me"),
]