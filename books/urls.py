from django.urls import path
from . import views

urlpatterns = [
    # Livros
    path("books/", views.books_list_api, name="books_list_api"),
    path("books/list/", views.books_list, name="books_list"),

    # Leitura por página (vai ficar /api/read/<book>/<page>/)
    path("read/<int:book_id>/<int:page_number>/", views.read_page_api, name="read_page_api"),
]