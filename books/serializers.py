from django.utils import timezone
from rest_framework import serializers
from .models import Book, Tag, BookComment, BookAnnotation


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class BookSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    cover = serializers.ImageField(read_only=True)
    pdf_file = serializers.FileField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id", "title", "author", "genre", "release_year",
            "description", "book_type", "total_pages",
            "cover", "pdf_file", "tags", "created_at"
        ]


def _user_label(u):
    if not u:
        return ""
    return getattr(u, "username", "") or getattr(u, "email", "") or str(u)


class BookCommentSerializer(serializers.ModelSerializer):
    user_label = serializers.SerializerMethodField()
    created_at_display = serializers.SerializerMethodField()

    class Meta:
        model = BookComment
        fields = [
            "id",
            "book",
            "page_number",
            "text",
            "user_label",
            "created_at",
            "created_at_display",
        ]
        read_only_fields = ["id", "user_label", "created_at", "created_at_display", "book"]

    def get_user_label(self, obj):
        return _user_label(obj.user)

    def get_created_at_display(self, obj):
        dt = obj.created_at
        try:
            dt = timezone.localtime(dt)
        except Exception:
            pass
        return dt.strftime("%Y-%m-%d %H:%M")


class BookAnnotationSerializer(serializers.ModelSerializer):
    user_label = serializers.SerializerMethodField()
    created_at_display = serializers.SerializerMethodField()

    class Meta:
        model = BookAnnotation
        fields = [
            "id",
            "book",
            "page_number",
            "x",
            "y",
            "text",
            "user_label",
            "created_at",
            "created_at_display",
        ]
        read_only_fields = ["id", "user_label", "created_at", "created_at_display", "book"]

    def get_user_label(self, obj):
        return _user_label(obj.user)

    def get_created_at_display(self, obj):
        dt = obj.created_at
        try:
            dt = timezone.localtime(dt)
        except Exception:
            pass
        return dt.strftime("%Y-%m-%d %H:%M")