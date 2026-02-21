from django.contrib import admin
from .models import ReadingProgress

@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "book", "current_page", "updated_at")