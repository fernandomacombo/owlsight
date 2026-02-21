from django.contrib import admin
from .models import Book, Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("name",)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "book_type", "created_at")
    list_filter = ("book_type", "genre", "tags")
    search_fields = ("title", "author", "genre")
    filter_horizontal = ("tags",)