from rest_framework import serializers
from .models import Book, Tag

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