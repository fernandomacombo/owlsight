from django.contrib import admin
from .models import UploadTest

@admin.register(UploadTest)
class UploadTestAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")