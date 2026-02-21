from django.conf import settings
from django.db import models

class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    class BookType(models.TextChoices):
        FREE = "free", "Free"
        PREMIUM = "premium", "Premium"

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=120, blank=True)
    genre = models.CharField(max_length=80, blank=True)
    release_year = models.PositiveIntegerField(null=True, blank=True)

    description = models.TextField(blank=True)

    book_type = models.CharField(
        max_length=10,
        choices=BookType.choices,
        default=BookType.FREE,
    )

    total_pages = models.PositiveIntegerField(null=True, blank=True)

    # uploads -> Backblaze B2
    cover = models.ImageField(upload_to="media/covers/", blank=True, null=True)
    pdf_file = models.FileField(upload_to="media/pdfs/", blank=True, null=True)

    tags = models.ManyToManyField(Tag, blank=True, related_name="books")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ReadingProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="progresses")
    current_page = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "book")

    def __str__(self):
        return f"{self.user} - {self.book} (p{self.current_page})"


class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="ratings")
    stars = models.PositiveSmallIntegerField()  # 1..5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "book")