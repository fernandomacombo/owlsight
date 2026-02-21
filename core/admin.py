from django.contrib import admin
from .models import Book, Tag, ReadingProgress, Rating

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ("name",)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "book_type", "created_at")
    list_filter = ("book_type", "genre", "tags")
    search_fields = ("title", "author", "genre")
    filter_horizontal = ("tags",)

@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "book", "current_page", "updated_at")
    search_fields = ("user__username", "book__title")

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "book", "stars", "created_at")
    list_filter = ("stars",)