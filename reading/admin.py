from django.contrib import admin
from .models import ReadingProgress, Favorite, Rating


@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "book", "last_page", "progress_percent", "updated_at")
    list_filter = ("updated_at",)
    search_fields = ("user__username", "user__email", "book__title")
    autocomplete_fields = ("user", "book")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "book", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email", "book__title")
    autocomplete_fields = ("user", "book")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "book", "stars", "updated_at")
    list_filter = ("stars", "updated_at")
    search_fields = ("user__username", "user__email", "book__title")
    autocomplete_fields = ("user", "book")