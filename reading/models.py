from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


class ReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reading_progress")
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE, related_name="progress")
    last_page = models.PositiveIntegerField(default=1)
    progress_percent = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "book")


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "book")


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE, related_name="ratings")
    stars = models.PositiveSmallIntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "book")


# ✅ NOVO: cada página como imagem (vai para o mesmo storage do Django: Backblaze)
class BookPageImage(models.Model):
    book = models.ForeignKey("books.Book", on_delete=models.CASCADE, related_name="page_images")
    page_number = models.PositiveIntegerField()
    image = models.ImageField(upload_to="pages/", blank=True, null=True)  # ✅ permitir null

    class Meta:
        unique_together = ("book", "page_number")
        indexes = [models.Index(fields=["book", "page_number"])]

    def __str__(self):
        return f"{self.book_id} p.{self.page_number}"
    
