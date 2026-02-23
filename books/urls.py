from django.urls import path
from . import views

urlpatterns = [
    # Livros
    path("books/", views.books_list_api, name="books_list_api"),
    path("books/list/", views.books_list, name="books_list"),

    # Leitura por página
    path("read/<int:book_id>/<int:page_number>/", views.read_page_api, name="read_page_api"),

    # ✅ Comments / Annotations (DRF)
    path("books/<int:book_id>/comments/", views.book_comments_api, name="book_comments_api"),
    path("books/<int:book_id>/annotations/", views.book_annotations_api, name="book_annotations_api"),

    # ✅ Delete annotation (opcional)
    path("books/annotations/<int:annotation_id>/", views.book_annotation_delete_api, name="book_annotation_delete_api"),
]