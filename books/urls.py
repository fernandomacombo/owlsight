from django.urls import path
from . import views

urlpatterns = [
    path("books/", views.books_list_api, name="books_list_api"),
    path("books/list/", views.books_list, name="books-list"),
]