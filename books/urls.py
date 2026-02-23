from django.urls import path
from . import views

urlpatterns = [
    # Livros
    path("books/", views.books_list_api, name="books_list_api"),
    path("books/list/", views.books_list, name="books_list"),

    # Leitura por página
    path("read/<int:book_id>/<int:page_number>/", views.read_page_api, name="read_page_api"),

    # Comentários
    path("books/<int:book_id>/comments/", views.book_comments_api, name="book_comments_api"),

    # Anotações
    path("books/<int:book_id>/annotations/", views.book_annotations_api, name="book_annotations_api"),
    path("books/annotations/<int:annotation_id>/", views.book_annotation_delete_api, name="book_annotation_delete_api"),

    # Unlock por partilha (free)
    path("books/<int:book_id>/unlock-share/", views.book_unlock_share_api, name="book_unlock_share_api"),
]