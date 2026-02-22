from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("books/", views.books, name="books"),
    path("users/", views.users, name="users"),
    path("settings/", views.settings_view, name="settings"),
]